# Solution: implement and benchmark `strcpy`, `strcat`, `memcpy`

This is the reference implementation of Part A of the string-functions exercise in [`01-string-functions`](../../01-string-functions).

Only `mystring.c` differs from the exercise directory — `mystring.h`, `test_mystring.c`, `bench.c` and the `Makefile` are the files students never touch.

**Part B is deliberately not solved here.** The exercise asks you to write your own `my_tests.c` before running the provided suite, and deciding what "correct" means in code is the actual skill being taught. There is no `my_tests.c` in this directory for the same reason the exercise README says "No solutions here — that is the exercise."

## The four functions

**`my_strlen`** walks to the `'\0'` and returns the distance covered. The terminator is not counted, so the loop stops *on* it rather than after it.

**`my_strcpy`** puts the assignment in the loop condition:

```c
while ((*d++ = *src++) != '\0')
	;
```

The byte is copied first and the copied value tested second, so the `'\0'` is written and *then* ends the loop. Copying the terminator is what makes `dest` a string rather than a pile of bytes. The return value is `dest`, not the end of it — easy to get wrong, and the test suite checks it.

**`my_strcat`** finds the end of `dest` and copies `src` there:

```c
my_strcpy(dest + my_strlen(dest), src);
```

One line, and it hides the whole point of the exercise — see below.

**`my_memcpy`** takes typed pointers first, because `void *` can be neither dereferenced nor advanced. `unsigned char` is the right choice: exactly one byte, no padding or trap representations. `n` is the only stopping condition, so an embedded `'\0'` is copied straight through, and `while (n-- > 0)` handles `n == 0` without a special case.

## Why `my_strcat` is quadratic

`my_strlen(dest)` rescans the whole of `dest` on **every** call, because a C string does not carry its length. By call *i* the string is already `16 × i` bytes long, so each call walks `16 × i` bytes just to find where to write 16 more. Appending N chunks scans ≈ `8N²` bytes to copy `16N` bytes of data.

The fix is not a faster loop — it is not throwing the length away, which is what the `my_memcpy` variant in `bench.c` does by tracking the offset itself.

## Build and check

```console
make test
```

```text
25/25 checks passed
All good. Now run: make bench
```

```console
make bench
```

Measured on this machine (times in ms; your numbers will differ, **the shape is the point**):

```text
       N     my_strcat     my_memcpy   libc strcat   libc memcpy     ratio
                                                                   cat/cpy
    1000         2.20          0.02          0.12          0.00      144.8x
    2000         8.51          0.03          0.41          0.00      291.9x
    4000        33.98          0.06          2.05          0.00      563.5x
    8000       124.42          0.10          6.13          0.00     1210.6x
   16000       479.91          0.24         28.07          0.01     1993.1x
   32000      1816.86          0.39         99.57          0.01     4713.7x
```

`my_strcat` takes 4× longer every time N doubles — the signature of O(N²). `my_memcpy` merely doubles: O(N). The ratio column is not a constant but grows without bound, which is what "different complexity" means.

Note the `libc strcat` column: hand-written, SIMD, ~18× faster than the byte loop — and still 4× per doubling. A better constant factor cannot buy a better algorithm, because the missing length is a property of the interface, not of the implementation.
