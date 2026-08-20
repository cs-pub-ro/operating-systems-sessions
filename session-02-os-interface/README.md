# Session 02: The Operating System Interface

## Learning objectives

By the end of this session you should be able to:

* Explain what a system call is and how a user-space program reaches the kernel through it.
* Describe the x86-64 Linux system call calling convention (registers used for the number, arguments, and the `syscall` instruction).
* Implement raw syscall wrappers (`my_syscall`, `my_write`, `my_getpid`, `my_nanosleep`) using inline assembly.
* Build higher-level helpers (`my_puts`, `my_sleep`) on top of your own syscall wrappers.
* Use `strace` to confirm which system calls a program actually performs.
* Plug a custom output hook (`_putchar`) into a portable `printf` implementation.

## Prerequisites and required tools

* Session 01 concepts: the software stack, and dynamic vs static linking.
* Basic familiarity with C pointers and function pointers.
* A Linux environment with `gcc`, `make`, and `strace` installed.
* No prior assembly experience is required; the inline assembly is provided or explained in each task.

## Task order

The demo is solved together with the teaching assistant at the start of the session.
Exercises are solved individually or in teams, in the numeric order shown below.
Bonus exercises are optional and can be tackled in any order once the core exercises are done.

| Order | Task | Type | Estimated time | Objective |
| --- | --- | --- | --- | --- |
| 1 | [`demo-puts-write`](demo-puts-write) | Demo | 15 min | Walk through the three-layer pattern: `my_puts` over `my_write` over `my_syscall`. |
| 2 | [`01-getpid`](01-getpid) | Core | 20 min | Implement the `getpid` syscall wrapper. |
| 3 | [`02-nanosleep`](02-nanosleep) | Core | 25 min | Implement `nanosleep` and a libc-style `sleep()` built on top of it. |
| 4 | [`bonus-clock_gettime`](bonus-clock_gettime) | Bonus | 30 min | Implement `clock_gettime` and a libc-style `time()` built on top of it. |
| 5 | [`bonus-printf`](bonus-printf) | Bonus | 25 min | Implement `_putchar` so a portable `printf` implementation writes through the `write` syscall. |

Reference solutions for every task are available in [`solutions/`](solutions).
The [`printf/`](printf) directory contains the third-party portable `printf` implementation used by `bonus-printf`; it is support code, not an exercise on its own.
</content>
