# Solution: the program that is right and still broken

This is the reference (leak-free) implementation of the longest-word exercise in [`02-longest-word`](../../02-longest-word).

## The bug

`tracker_offer()` replaced the longest word seen so far with a fresh `strdup()`:

```c
t->longest = strdup(word);
```

A pointer variable holds exactly one address.
Overwriting `t->longest` dropped the only reference to the previous heap copy, so every intermediate winner was leaked — the program's output was correct the whole time, and `main()` did dutifully `free()` the final word, but every winner before it was already unreachable.

The fix releases the old string before taking ownership of the new one; see the `FIX` comment in `main.c`.
`free(NULL)` is legal and does nothing, so the very first word needs no special case.

The rule to remember: **the struct owns the string it points to.**
Overwriting an owning pointer without releasing what it pointed to first drops the only reference to that block — after that, no code in the universe can free it.

Files:

* `main.c` — the fixed implementation.
* `input.txt` — the 21 sample words.

## Build and run

```console
make
./longest < input.txt
```

```text
read 21 words
longest word: extraordinarily (15 characters)
```

Same output as the buggy version — that is the point of the exercise.
The difference only shows under Valgrind:

```console
valgrind --leak-check=full ./longest < input.txt
```

```text
==2745183== HEAP SUMMARY:
==2745183==     in use at exit: 0 bytes in 0 blocks
==2745183==   total heap usage: 6 allocs, 6 frees, 8,225 bytes allocated
==2745183==
==2745183== All heap blocks were freed -- no leaks are possible
==2745183==
==2745183== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

Same allocation count as before, but every block now has a matching `free`.
