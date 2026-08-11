# Demo: `printf` vs `write`

So far we have talked about libraries and the software stack as if the C library were just a bag of useful functions.
This demo looks at what one of those functions actually costs.

`printf` sits at the **top** of the C library's output stack.
Underneath it there is a whole machine: it parses your format string, it manages a `FILE` object, it keeps a buffer — and at the very **bottom**, it calls `write`.

`write` is the other end of the stack: a thin, low-level output function.
No formatting, no buffering.
Every call hands your bytes straight out of your program to the operating system.

So `printf` does strictly *more* work than `write`.
**Which one is faster?**

Write down your guess.
Then type out the two programs below and find out.

> All the numbers below are from Ubuntu 24.04 / gcc 13.3 / x86-64.
> Yours will be different, and they will wobble by 10–20% between runs on the same machine.
> **The ratios are the point, not the digits.**
> If a result surprises you, run it three times before believing it.

## Step 1 — the `printf` version

Type this into **`printf_demo.c`**.
It is the whole program.

```C
#include <stdio.h>

#define N 1000000

const char *line = "hello from the operating systems lab\n";

int main(void)
{
	/* Switches stdout's buffer OFF. Comment it out to switch it back on. */
	setvbuf(stdout, NULL, _IONBF, 0);

	for (long i = 0; i < N; i++)
		printf("%s", line);

	return 0;
}
```

Build it and time it:

```console
gcc -O0 -Wall -Wextra -o printf_demo printf_demo.c
time ./printf_demo > /dev/null
```

```text
real	0m0.288s
user	0m0.157s
sys	0m0.131s
```

**Always redirect to `/dev/null`.**
Otherwise you are timing your terminal drawing a million lines, not your program.

## Step 2 — the `write` version

Now **`write_demo.c`**.
Same line, same million iterations, no C library on top:

```C
#include <string.h>
#include <unistd.h>

#define N 1000000

const char *line = "hello from the operating systems lab\n";

int main(void)
{
	size_t len = strlen(line);

	for (long i = 0; i < N; i++)
		write(1, line, len); /* 1 is stdout */

	return 0;
}
```

```console
gcc -O0 -Wall -Wextra -o write_demo write_demo.c
time ./write_demo > /dev/null
```

```text
real	0m0.193s
user	0m0.063s
sys	0m0.129s
```

**`write` wins — 0.19 s against 0.29 s.**
The low-level function beat the library by 50%, exactly as you would expect: `printf` does more work, so `printf` is slower.

Case closed?

## Step 3 — comment out one line

Go back to `printf_demo.c` and comment out the `setvbuf` line:

```C
	/* setvbuf(stdout, NULL, _IONBF, 0); */
```

Change nothing else.
Rebuild and run it again:

```console
gcc -O0 -Wall -Wextra -o printf_demo printf_demo.c
time ./printf_demo > /dev/null
```

```text
real	0m0.062s
user	0m0.060s
sys	0m0.002s
```

**0.06 s.**

The same program, minus one line, is now **~5× faster than it was** — and **3× faster than `write`**, which does far less work.
Nothing else changed.
The loop is identical, the output is identical, the compiler flags are identical.

| | real | user | sys |
| --- | ---: | ---: | ---: |
| `printf`, `setvbuf` line **active** | 0.29 s | 0.16 s | 0.13 s |
| `write` | 0.19 s | 0.06 s | 0.13 s |
| `printf`, `setvbuf` line **commented out** | **0.06 s** | 0.06 s | **0.00 s** |

So: is `printf` faster than `write`, or slower?
**Both.**
The question was wrong.
One line decides it, and that line is about *buffering*.

## Why — watch it happen

`strace` shows every `write` your program performs.
A million of them is too many to look at, so set `N` to **20** in both programs and rebuild.

With the `setvbuf` line **active** (buffer off):

```console
strace -e trace=write ./printf_demo > /dev/null
```

```text
write(1, "hello from the operating systems"..., 37) = 37
write(1, "hello from the operating systems"..., 37) = 37
write(1, "hello from the operating systems"..., 37) = 37
...20 of them...
```

Twenty lines, twenty calls of 37 bytes.
`write_demo` does exactly the same thing.

Now with the `setvbuf` line **commented out** (buffer on):

```text
write(1, "hello from the operating systems"..., 740) = 740
```

**One call. 740 bytes.**
That is 20 × 37 — the whole run delivered in a single trip, at the very end.

That is the entire demo.
`printf` did not send your first line when you asked it to.
It copied the bytes into a 4096-byte buffer inside your process and waited until it had a worthwhile amount to hand over.

Put `N` back to 1 000 000 and count them (this takes a few seconds — `strace` slows everything down, so trust the *count*, not the clock):

```console
strace -e trace=write ./printf_demo 2>&1 >/dev/null | grep -c '^write(1,'
```

**9034.**
A million lines of 37 bytes is 37 MB; at 4096 bytes per call, that is 9034 calls.
Against a million for the unbuffered version — **110× fewer.**

### The measurement that explains everything

**A `write` call costs roughly the same whether it carries 37 bytes or 4096.**
The expense is in *making the call at all*, not in the amount of data.
So:

* `write_demo` and unbuffered `printf_demo` both make **1 000 000 calls** — and look at the table: their `sys` times are **identical** (0.13 s).
  Of course they are.
  They do the same thing at the bottom.
* Buffered `printf_demo` makes **9034** — and its `sys` time collapses to **0.00 s**.

`sys` is time spent inside the operating system, working on your program's behalf.
That column *is* the call count, and it is why the answer flipped.

(*Why* a single `write` costs so much more than an ordinary function call in your own code is a story for a later session.
For now, take it as measured.)

### And where does the library's cost show up?

In the `user` column — time spent running your code and the library's code:

* `write_demo`: **0.06 s** — just the loop.
* unbuffered `printf_demo`: **0.16 s** — the same loop, plus 0.10 s of `printf` parsing `"%s"` a million times, running `vfprintf`'s general-purpose engine (it must be ready for `%d`, `%f`, width, precision, locale…), and locking the `FILE` object on every call.

That 0.10 s is what the abstraction costs.
It is real, and you can see it.

## The two lessons

> **1. Buffering beats being close to the metal.**
> `printf` wins not by being clever, but by *avoiding* the expensive thing.
> It pays a real price (0.10 s of library overhead) to make 9034 calls instead of a million — and that trade wins by 3×.
> Buffering is not an implementation detail of `printf`; it is the reason `printf` is shaped the way it is.

> **2. Take the buffer away and the abstraction is pure overhead.**
> Unbuffered `printf` pays for the library *and* for every expensive call underneath.
> It is the worst of both worlds — the only version here that is slower than doing it yourself.

`printf` is not "fast" or "slow".
Its buffer is.

## One more thing: why the terminal feels slow

You never call `setvbuf` in real code — so who chose the buffering?

**The C library did, by looking at where stdout goes.**
Into a file or a pipe: big 4096-byte buffer, the fast case you just measured.
Onto a terminal: it switches to flushing on every `\n`, which is one call per line — the slow case, by default, whenever a human is watching.

Try it.
Comment out `setvbuf`, set `N` to 5000, and run it *without* redirecting:

```console
./printf_demo
```

Same binary.
Same buffer.
Much slower, because of where the bytes were going.

It also explains this classic:

```C
printf("about to crash");   /* no \n */
abort();                    /* the message never appears */
```

The bytes were still sitting in `printf`'s buffer, inside your process, when it died.
They never left.
`write` would not have lost them — and that is exactly why `stderr` is unbuffered by default: a message you never see is worse than a slow one.

## Things to try

1. **Change the buffer size.**
   Replace the `setvbuf` line with:

   ```C
	static char buf[64];
	setvbuf(stdout, buf, _IOFBF, sizeof(buf));
   ```

   Then try `buf[65536]`.
   Time each, and check the call sizes with `strace`.
   Where do the gains stop, and why?

   > Careful: `setvbuf(stdout, NULL, _IOFBF, 64)` — with `NULL` instead of a real array — **silently ignores your size** and keeps the 4096-byte default.
   > Read `man setvbuf` and find the sentence that says so.
   > Then note that nothing warned you: it compiled, it ran, it did something other than what you asked.
   > `strace` is how you catch it.
1. Add `fflush(stdout);` inside the loop, after the `printf`, with the `setvbuf` line commented out.
   Predict the time *before* you run it.
   (Remember the loop needs `{ }` around two statements now.)
1. `./write_demo > out.txt` versus `> /dev/null`.
   A real file is more work — does the *ranking* change?
1. Write a third program: a `write` loop that fills your own 4096-byte buffer first and only calls `write` when it is full.
   That is `printf`'s trick, without `printf`.
   How close to 0.06 s can you get, and what does the difference tell you about what stdio does for its money?
1. `printf` writes 37 bytes per line, but `strace` showed 4096-byte calls — which means lines get **split across** calls.
   Find a split in the output of `strace -e trace=write ./printf_demo > /dev/null` with `N` set to 200.

## Check yourself

* `printf` does more work than `write`, and is 3× faster.
  Explain in one sentence.
* Unbuffered `printf` and `write_demo` have the same `sys` time but very different `user` time.
  Why each?
* Your program writes a log line every few seconds and crashes on the bug you are hunting.
  Which version do you want, and why is it the *slowest* one?
* `write` returned successfully.
  Are your bytes on the disk? (Think about it — we will come back to this.)
