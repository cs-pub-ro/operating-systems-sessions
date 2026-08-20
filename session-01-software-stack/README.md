# Session 01: The Software Stack

## Learning objectives

By the end of this session you should be able to:

* Explain the layers between a C program and the kernel: application code, C library, and system calls.
* Implement basic string-handling functions (`strlen`, `strcpy`, `strcat`, `memcpy`) and reason about their algorithmic cost.
* Compare buffered (`printf`) and unbuffered (`write`) output, and explain the buffering trade-off.
* Build a C program as a dynamically-linked executable, a statically-linked executable, and against a shared or static library.
* Explain the difference between static linking (`.a`, `ar`) and dynamic linking (`.so`), including symbol resolution via the PLT/GOT.

## Prerequisites and required tools

* Prior knowledge of C syntax: pointers, arrays, functions, basic `<string.h>` usage.
* A Linux environment with `gcc`, `make`, `ar`, `ldd`, `nm`, `objdump`, and `strace` installed.
* Comfort with the command line (running commands, redirecting output, reading `man` pages).

## Task order

The demos are solved together with the teaching assistant at the start of the session.
Exercises are solved individually or in teams, in the numeric order shown below.
Bonus exercises are optional and can be tackled in any order once the core exercises are done.

| Order | Task | Type | Estimated time | Objective |
| --- | --- | --- | --- | --- |
| 1 | [`demo-printf-vs-write`](demo-printf-vs-write) | Demo | 15 min | See why `printf` can be faster or slower than `write` depending on buffering. |
| 2 | [`demo-copy-string`](demo-copy-string) | Demo | 10 min | Compare `strcat`-based and `strcpy`-based string building. |
| 3 | [`01-string-functions`](01-string-functions) | Core | 30 min | Implement `strlen`, `strcpy`, `strcat`, and `memcpy` from scratch. |
| 4 | [`02-stream-ciphers`](02-stream-ciphers) | Core | 30 min | Build the same program as a dynamic executable, a static executable, a shared library, and a static library. |
| 5 | [`bonus-static-vs-dynamic`](bonus-static-vs-dynamic) | Bonus | 45 min | Package your string functions as `libmystring`, measure static vs dynamic call and start-up cost. |
| 6 | [`bonus-per-stream-cipher-exec`](bonus-per-stream-cipher-exec) | Bonus | 30 min | Split the cipher program into one dedicated executable per cipher, in all four link formats. |

Reference solutions for every task are available in [`solutions/`](solutions).
</content>
