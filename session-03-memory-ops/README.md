# Session 03: Memory Operations

## Learning objectives

By the end of this session you should be able to:

* Copy data using a static/global buffer, a heap buffer (`malloc`/`free`), and a memory-mapped file (`mmap`), and explain the trade-offs of each.
* Free every heap allocation on every code path, including early returns.
* Build a growable in-memory data structure using `malloc` and `realloc` with a chunked growth strategy.
* Shrink a dynamic array's capacity safely when its usage drops, without invalidating live data.

## Prerequisites and required tools

* Session 01 and 02 concepts: the software stack and system calls.
* Comfort with C pointers, `struct`s, and file I/O (`open`, `read`, `write`, or `<stdio.h>` equivalents).
* A Linux environment with `gcc`, `make`, and `valgrind` installed.

## Task order

The demo is solved together with the teaching assistant at the start of the session.
It is presented in three variants, of increasing sophistication, and should be worked through in order.
The exercise is solved individually or in teams.
The bonus exercise is optional.

| Order | Task | Type | Estimated time | Objective |
| --- | --- | --- | --- | --- |
| 1 | [`demo-copy-file/global-buffer`](demo-copy-file/global-buffer) | Demo | 10 min | Copy a file using a static global buffer and `memcpy`. |
| 2 | [`demo-copy-file/malloc`](demo-copy-file/malloc) | Demo | 10 min | Copy a file using a heap buffer, freeing it on every return path. |
| 3 | [`demo-copy-file/mmap`](demo-copy-file/mmap) | Demo | 15 min | Copy a file by mapping both source and destination with `mmap`. |
| 4 | [`01-in-memory-db`](01-in-memory-db) | Core | 40 min | Build a growable in-memory database from stdin records using chunked `realloc`. |
| 5 | [`bonus-in-mem-database`](bonus-in-mem-database) | Bonus | 35 min | Extend the database with record deletion and capacity shrinking. |

Reference solutions for every task are available in [`solutions/`](solutions).
</content>
