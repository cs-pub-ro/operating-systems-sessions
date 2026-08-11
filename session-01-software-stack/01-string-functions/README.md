# Exercise: implement and benchmark `strcpy`, `strcat`, `memcpy`

In the `printf` vs `write` demo you saw that the C library is not magic: `printf` is ordinary code, with more layers under it than you might have guessed.
Now we go one level further down and write some of that ordinary code ourselves.

Then we measure it and find something surprising about `strcat`.

## Part A — implement

Fill in the four functions in **`mystring.c`**.
That is the only file you change.

| function | what it must do |
| --- | --- |
| `my_strlen` | length up to, not including, the `'\0'` |
| `my_strcpy` | copy a string, `'\0'` included; return `dest` |
| `my_strcat` | append to the string in `dest`; return `dest` |
| `my_memcpy` | copy exactly `n` bytes; knows nothing about `'\0'`; return `dest` |

**Do not call anything from `<string.h>`** — that is the whole point.
`mystring.c` deliberately does not include it.

Once you have written them, do **not** jump straight to the benchmark.
First convince yourself they actually work — that is Part B.

### Things to get right

* `my_strcpy` must copy the `'\0'`.
  If it does not, `dest` is not a string.
* `my_strcat` needs `dest` to *already* be a valid string.
  Appending to uninitialised memory is undefined behaviour, not an empty string.
* `my_memcpy` takes `void *`.
  You cannot dereference or do arithmetic on `void *` — assign to `unsigned char *` first.
* `my_memcpy` may assume the regions do not overlap.
  Handling overlap is `memmove`'s job. (Worth reading up on why both exist.)

## Part B — test it yourself

There is a ready-made test suite in this directory, and you will run it in a minute.
But **write your own tests first.**
Deciding what "correct" means, in code, before you trust your own work is the actual skill here — running someone else's tests is not.

### 1. Create the file

Make a new file called **`my_tests.c`**.
It needs `main()`, and it needs to include `mystring.h` so it knows what your functions look like.

Here is a complete, working starting point.
It tests **one** function — `my_strlen`.
The other three are yours.

```C
/* my_tests.c - my own tests for mystring.c */

#include <stdio.h>

#include "mystring.h"

int main(void)
{
        /* --- my_strlen --- */
        printf("my_strlen(\"\")      = %zu   (expected 0)\n", my_strlen(""));
        printf("my_strlen(\"a\")     = %zu   (expected 1)\n", my_strlen("a"));
        printf("my_strlen(\"hello\") = %zu   (expected 5)\n", my_strlen("hello"));

        /* --- my_strcpy: your turn --- */

        /* --- my_strcat: your turn --- */

        /* --- my_memcpy: your turn --- */

        return 0;
}
```

> `my_strlen` returns a `size_t`, so it is printed with `%zu`, not `%d`.
> Using the wrong conversion here is undefined behaviour, and `-Wall` will tell you about it.

### 2. Compile it

Two source files now: yours and the one with the functions in it.
Hand both to gcc:

```console
gcc -Wall -Wextra -std=c11 -o my_tests my_tests.c mystring.c
```

Then run it:

```console
./my_tests
```

You can also do it in two stages — **compile** each `.c` into an object file, then **link** the object files into a program:

```console
gcc -Wall -Wextra -std=c11 -c mystring.c -o mystring.o
gcc -Wall -Wextra -std=c11 -c my_tests.c -o my_tests.o
gcc -o my_tests my_tests.o mystring.o
./my_tests
```

Both produce the same program.
The one-line version just does both stages for you.
The split version is worth remembering — it is exactly what the bonus exercise builds on, and it is why `mystring.c` can be compiled once and reused by several programs.

### 3. Now test the other three

No solutions here — that is the exercise.
Some things worth deciding for yourself:

* **`my_strcpy`** — you need somewhere to copy *to*.
  Declare a `char buf[64];`.
  After the copy, does `buf` hold what you expect?
  Print it.
  Did the function **return** `buf`?
  What happens with an empty string?
* **`my_strcat`** — `dest` must already be a valid string, so build one with `my_strcpy` first, then append.
  `"foo"` + `"bar"` should give `"foobar"`.
  What about appending to `""`?
  What about appending `""`?
* **`my_memcpy`** — copy 5 bytes and print them.
  Then the interesting ones: what should `n == 0` do?
  And what happens with `"ab\0cd"` and `n == 6` — does it copy straight through the `'\0'`, where `my_strcpy` would stop?

Compare each result against what the man page says (`man strcpy`, `man memcpy`) rather than against what your code happens to do.

### 4. Then run the provided suite

Once your own tests look right, check yourself against the 25 tests in `test_mystring.c`:

```console
make test
```

You should end at `25/25 checks passed`.
It also checks things that are awkward to eyeball: that you never write past the end of what you were asked to touch, and that `my_memcpy` copies straight through an embedded `'\0'`.

If it catches something your own tests missed, that is the interesting part — **go and work out which test case you did not think of, and why.**

## Part C — measure: `strcat` vs `memcpy`

Once the tests pass:

```console
make bench
```

Both columns build the **same** string: a 16-byte chunk appended N times.
The only difference is which function does the appending.

```C
/* with strcat */                    /* with memcpy */
dst[0] = '\0';                       size_t off = 0;
for (i = 0; i < n; i++)              for (i = 0; i < n; i++) {
        my_strcat(dst, CHUNK);               my_memcpy(dst + off, CHUNK, 16);
                                             off += 16;
                                     }
```

### Results

Ubuntu 24.04, gcc 13.3, times in ms.
Your numbers will differ; **the shape is the point.**

| N | `my_strcat` | `my_memcpy` | `libc strcat` | `libc memcpy` | strcat/memcpy |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 000 | 1.72 | 0.01 | 0.10 | 0.00 | 142× |
| 2 000 | 6.90 | 0.02 | 0.33 | 0.00 | 295× |
| 4 000 | 27.17 | 0.05 | 1.40 | 0.00 | 562× |
| 8 000 | 107.03 | 0.09 | 6.13 | 0.00 | 1 148× |
| 16 000 | 427.52 | 0.18 | 24.96 | 0.01 | 2 375× |
| 32 000 | 1 701.53 | 0.39 | 99.68 | 0.01 | 4 419× |

### Read the columns, not the numbers

**Every time N doubles, `my_strcat` takes 4× longer** (1.72 → 6.90 → 27.17 → 107 → 427 → 1701; that is 4.0×, 3.9×, 3.9×, 4.0×, 4.0×).
Time going up 4× when the input goes up 2× is the signature of **O(N²)**.

**`my_memcpy` merely doubles** (0.01 → 0.02 → 0.05 → 0.09 → 0.18 → 0.39).
That is **O(N)** — what you would expect from "append N chunks".

The ratio column is not a constant.
It *grows*: 142× at N=1 000, 4 419× at N=32 000.
Two functions with different complexity do not have a "ratio" — the gap widens forever.
Double N again and it gets 2× worse.

### Why is `strcat` quadratic?

Look at the signatures:

```C
char *strcat(char *dest, const char *src);
void *memcpy(void *dest, const void *src, size_t n);
```

`memcpy` is **told** how many bytes to copy.
`strcat` is not told where `dest` ends — so it has to **go and find out**, by walking `dest` from the beginning looking for the `'\0'`, on **every single call**.

By call number *i*, `dest` is already `16 × i` bytes long, so the scan costs `16 × i` steps just to find the place to write 16 bytes:

```text
scan 0 bytes,   append 16
scan 16 bytes,  append 16
scan 32 bytes,  append 16
...
scan 511 984 bytes, append 16     <- call 32 000
```

Total: `16 × (0 + 1 + 2 + ... + N-1)` ≈ **8N²** bytes scanned to copy 16N bytes of actual data.
At N=32 000 that is ~8 **billion** bytes walked to write half a megabyte.
Your loop is fine; the *information* is missing.

This is common enough to have a name: **"Schlemiel the Painter's algorithm"** — the painter who walks back to the paint can after every stroke, and gets slower the further down the road he gets.

> **The bug is in the API, not in your code.**
> A C string does not carry its length, so every function that needs the length must recompute it.
> This is why `strcat` in a loop is a classic performance bug, and why Pascal, Rust, Go and C++ `std::string` all store the length next to the bytes.

### The most important column: `libc strcat`

glibc's `strcat` is hand-written, uses SIMD, and is about **17× faster** than your byte loop (99.68 ms vs 1 701 ms at N=32 000).
Real speedup, real engineering.

**And it is still quadratic.**
Look at its column: 0.10 → 0.33 → 1.40 → 6.13 → 24.96 → 99.68.
Still 4× per doubling.
All that hand-tuning bought a better *constant factor*; it cannot buy a better *algorithm*, because the missing length is a property of the interface, not of the implementation.

Now compare the two extremes at N=32 000:

* glibc's expert, SIMD-optimised `strcat`: **99.68 ms**
* your naive, byte-at-a-time `my_memcpy`: **0.39 ms**

**Your "slow" code beats their fast code by 255×**, because you used an algorithm that does not throw the length away.

> **The lesson.**
> A better constant factor is worth ~17×.
> A better algorithm is worth ~4 400× and grows without bound.
> When something is slow, ask *what work is being repeated* before you ask *how to make the work faster*.
> "Rewrite it in assembly" would not have saved `strcat` here.

And note the direction: in the `printf` vs `write` demo, the library beat the naive hand-written code (buffering).
Here, the naive hand-written code beats the library (algorithm).
**Neither "use the library" nor "write it yourself" is the lesson. Measuring is.**

There is one more echo of the `printf` vs `write` demo here.
There, `printf` won by avoiding expensive work (calls to `write`) rather than by doing cheap work faster.
Here, `my_memcpy` wins by avoiding repeated work (rescanning the string) rather than by copying bytes faster.
Both times, the winner was the one that *did less* — not the one that was better optimised.

## Things to try

1. Add a `my_strcat_fast` that takes the current length as a parameter and returns the new one.
   Which column does it match?
1. Change `CHUNK` to 1 byte, then to 256.
   Does the *shape* change?
   Does the crossover point move?
1. Extend the sweep to N = 64 000 and predict `my_strcat`'s time first.
   (Try 128 000 only if you are patient — that is the point.)
1. `strncat` and `strlcat` also exist.
   Do they fix the quadratic problem?
   Why not?
1. Time `my_memcpy` vs `libc memcpy` on a single 1 MB copy.
   Now that the algorithms match, how big is the constant factor gap?
   What does glibc's do differently? (`objdump -d`, or read glibc's `memcpy-avx2-unaligned.S`.)

## Check yourself

* Without running it: you append 1 000 chunks and it takes 2 ms.
  Roughly how long for 4 000?
* Why can `memcpy` copy through an embedded `'\0'` when `strcpy` cannot?
* glibc's `strcat` is written by experts in assembly and is still 255× slower than your naive `my_memcpy` here.
  Explain that to someone in one sentence.
* You must keep the C API `char *strcat(char *, const char *)` exactly.
  Can you make it non-quadratic?
  What would you have to change?
