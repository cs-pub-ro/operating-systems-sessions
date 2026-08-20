# Session 04: Memory Debugging

## Learning objectives

By the end of this session you should be able to:

* Use `gdb` to set breakpoints and watchpoints, inspect variables, and read a backtrace.
* Use Valgrind's Memcheck tool to locate invalid reads/writes and memory leaks.
* Recognize common bug patterns: unsigned integer underflow, dangling pointers after `realloc`, uninitialized memory, broken linked-list removal, and off-by-one buffer allocation.
* Diagnose a bug from a compiled binary alone, without access to its source code.

## Prerequisites and required tools

* Session 03 concepts: heap allocation with `malloc`/`realloc`/`free`.
* A Linux environment with `gcc`, `make`, `gdb`, and `valgrind` installed.
* For the binary-only bonus exercise: `objdump`, `nm`, `readelf`, and Python.

## Task order

The demo is solved together with the teaching assistant at the start of the session.
Exercises are solved individually or in teams, in the numeric order shown below.
Bonus exercises are optional and can be tackled in any order once the core exercises are done.

| Order | Task | Type | Estimated time | Objective |
| --- | --- | --- | --- | --- |
| 1 | [`demo-in-memory-database`](demo-in-memory-database) | Demo | 25 min | Walk through fixing 3 bugs (underflow crash, dangling pointer after `realloc`, leaked buffer) in the session-03 database, using `gdb` and Valgrind. |
| 2 | [`01-grade-histogram`](01-grade-histogram) | Core | 20 min | Find and fix an off-by-one bucket write using a conditional breakpoint or watchpoint. |
| 3 | [`02-longest-word`](02-longest-word) | Core | 15 min | Find and fix a memory leak caused by reassigning a pointer without freeing the old allocation. |
| 4 | [`03-symbol-hash-table`](03-symbol-hash-table) | Core | 45 min | Find and fix three bugs in a hash table: uninitialized memory, a broken linked-list removal, and a leak. |
| 5 | [`bonus-json-parser`](bonus-json-parser) | Bonus | 40 min | Find and fix a heap buffer overflow caused by a missing NUL-terminator byte in a JSON parser. |
| 6 | [`bonus-binary-issue`](bonus-binary-issue) | Bonus | 45 min | Locate and patch a stack buffer overflow directly in a compiled binary, with no source code given. |

Reference solutions for every task are available in [`solutions/`](solutions).
</content>
