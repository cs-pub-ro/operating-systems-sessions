# Exercise 2: the program that is right and still broken

`main.c` reads whitespace-separated words from standard input and reports how
many there were and which one was the longest:

```sh
make
./longest < input.txt
```

```
read 21 words
longest word: extraordinarily (15 characters)
```

That is the correct answer. There is no crash, no warning from
`-Wall -Wextra`, and no wrong number anywhere. If the only thing you ever
checked was the output, you would ship this.

## Look at it with Valgrind

```sh
valgrind --leak-check=full ./longest < input.txt
```

Read the report and answer these questions before touching the code:

- How many blocks were allocated, and how many were freed?
- How many bytes are **definitely lost**, in how many blocks?
- Which function allocated them, and on which line? (The stack trace under the
  leak report is the *allocation* site: where the memory was born, not where it
  was lost.)

Then find the reason. The program keeps exactly one string on the heap at a
time — the longest word seen so far — and `main()` does `free()` it at the end.
So why is more than one block still outstanding when the program exits?

Two hints, if you need them:

- Count how many times a word in the input is longer than every word before
  it — that is how many heap copies the program makes. All but one of them
  left something behind.
- A pointer variable holds exactly one address. Ask what happens to the address
  that was in it a moment ago, when a new one is assigned on top.

## What "definitely lost" means

Valgrind sorts unfreed memory into categories, and the difference matters:

| Category | Meaning |
|----------|---------|
| **definitely lost** | at exit, no pointer to this block existed anywhere — it could never have been freed. A real leak; fix it. |
| **indirectly lost** | the block was only reachable through a definitely-lost one (e.g. the nodes hanging off a leaked list head). Fixing the parent usually fixes these too. |
| **possibly lost** | only a pointer to the *middle* of the block still existed. Sometimes fine, usually worth a look. |
| **still reachable** | you still had a pointer to it at exit but never freed it. Not a runaway leak, but sloppy: it hides real leaks in the noise, so free it anyway. |

## Your task

1. Identify the leak with Valgrind.
2. Fix it, keeping the program's output identical. The rule to apply: **the
   struct owns the string it points to.** Overwriting an owning pointer without
   releasing what it pointed to first drops the only reference to that block —
   after that, no code in the universe can free it.
3. Check your work:

```sh
valgrind --leak-check=full ./longest < input.txt
```

```
==2745183== HEAP SUMMARY:
==2745183==     in use at exit: 0 bytes in 0 blocks
==2745183==   total heap usage: 6 allocs, 6 frees, 8,225 bytes allocated
==2745183==
==2745183== All heap blocks were freed -- no leaks are possible
==2745183==
==2745183== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

Same allocation count as before, but every block now has a matching `free`.

Also make sure you did not break the corner cases, which is easy to do while
juggling `free`:

```sh
printf 'aaa\n' | ./longest                 # one word, one allocation
printf '' | ./longest                      # no words at all: free(NULL) is legal
printf 'zz\naaa\nbbbb\naaaaa\n' | ./longest  # a new winner every time
```

Run each of them under Valgrind too. `free(NULL)` is explicitly allowed by the
standard and does nothing, so the empty case needs no special handling — but a
*double* free of the same non-NULL pointer is undefined behaviour, and Valgrind
will report it loudly as an "Invalid free".

## Takeaway

This program was *observably correct*. The leak is small — 17 bytes — and on a
short input it is harmless; the kernel reclaims everything when the process
exits anyway. Now imagine the same function inside a service that processes
words for months without restarting.

That is why "it prints the right thing" is not a definition of correctness in C,
and why running Valgrind should be as automatic as compiling. Make
`valgrind --leak-check=full` part of how you test every assignment, not
something you reach for after a crash.
