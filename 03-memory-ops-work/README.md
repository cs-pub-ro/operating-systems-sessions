# Session 03: Memory Operations

This session is about moving and storing data in memory -- static buffers, the heap, and memory-mapped files -- and doing it without leaking.

* Copying data with a global buffer, a heap buffer, and `mmap`.
* Freeing every allocation on every path, including the error paths.
* Growing and shrinking a dynamic structure with `malloc` and `realloc`.
* Proving a program leaks nothing, with Valgrind.

## Learning objectives

By the end of this session you should be able to:

* Copy data using a static global buffer, a heap buffer (`malloc`/`free`), and a memory-mapped file (`mmap`), and explain the trade-offs of each.
* Free every heap allocation on every code path, including early returns and error paths.
* Build a growable in-memory data structure using `malloc` and `realloc` with a chunked growth strategy.
* Use `realloc` correctly, including what happens to your data when it fails.
* Shrink a dynamic array safely when its usage drops, without invalidating live data.
* Use Valgrind to prove that a program leaks nothing.

## Prerequisites and required tools

* Session 01 and 02 concepts: the software stack, and system calls.
* Comfort with C pointers, `struct`s, and file I/O (`open`/`read`/`write` or the `<stdio.h>` equivalents).
* A Linux environment with `gcc`, `make` and `valgrind` installed.

Before the session, check that your machine has these tools with the [setup script](../scripts/check-prerequisites.sh):

```console
./scripts/check-prerequisites.sh -s 3
```

## Getting the lab archive

Download [`03-memory-ops.zip`](https://github.com/cs-pub-ro/operating-systems-sessions/raw/lab-archives/03-memory-ops.zip), then unzip it and change into the directory it creates:

```console
unzip 03-memory-ops.zip
cd 03-memory-ops
```

Work inside that directory for the rest of the session.

## Task order

The demo comes first, solved together with the teaching assistant.
It has three variants of the same program, of increasing sophistication, worked through in order.
The core exercise is solved individually or in teams; the bonus is optional.

| Order | Task | Type | Objective |
| --- | --- | --- | --- |
| 1 | [`demo-copy-file/global-buffer`](demo-copy-file/global-buffer) | Demo | Copy a file through a static global buffer. |
| 2 | [`demo-copy-file/malloc`](demo-copy-file/malloc) | Demo | The same program with a heap buffer, freed on every path. |
| 3 | [`demo-copy-file/mmap`](demo-copy-file/mmap) | Demo | The same program again, with both files mapped into memory. |
| 4 | [`01-in-memory-db`](01-in-memory-db) | Core | Build a growable in-memory database using chunked `realloc`. |
| 5 | [`bonus-in-mem-database`](bonus-in-mem-database) | Bonus | Extend it with record deletion and capacity shrinking. |

`bonus-in-mem-database` starts from **your finished `main.c`** of `01-in-memory-db`, so do the core exercise first.

Each exercise directory has a `README.md` with the task itself.
Where there is also a `FURTHER.md`, it holds optional extensions and questions to dig into once the task is done.
