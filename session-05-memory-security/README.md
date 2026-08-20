# Session 05: Memory Security

## Learning objectives

By the end of this session you should be able to:

* Explain how a heap buffer overflow can corrupt an adjacent variable or structure field.
* Craft an overflow payload that sets a target value precisely, including endianness considerations.
* Explain how hijacking a function pointer on the heap can redirect control flow.
* Explain what a use-after-free bug is and how allocator reuse (tcache) can make it exploitable.
* Combine an information leak with a heap overflow to defeat ASLR.

## Prerequisites and required tools

* Session 04 concepts: heap layout and using `gdb` to inspect memory.
* A Linux environment with `gdb` and `objdump`.
* Basic familiarity with two's complement, endianness, and reading disassembly.

## Task order

The demos are solved together with the teaching assistant at the start of the session, as warm-ups.
Exercises are solved individually or in teams, in the numeric order shown below, with each one building on the previous one's technique.
Bonus exercises are optional and are more difficult; tackle them in any order once the core exercises are done.

| Order | Task | Type | Estimated time | Objective |
| --- | --- | --- | --- | --- |
| 1 | [`demo-heap-0`](demo-heap-0) | Demo | 15 min | Overflow a heap buffer to flip an adjacent `lock_state` variable. |
| 2 | [`demo-heap-1`](demo-heap-1) | Demo | 15 min | Overflow a heap buffer to set an adjacent variable to one specific value. |
| 3 | [`01-cylab-heap-0`](01-cylab-heap-0) | Core | 20 min | Solve a basic heap overflow challenge individually. |
| 4 | [`02-cylab-heap-1`](02-cylab-heap-1) | Core | 25 min | Solve a heap overflow challenge that requires a precise target value. |
| 5 | [`03-cylab-heap-2`](03-cylab-heap-2) | Core | 30 min | Overflow into a function pointer and hijack control flow. |
| 6 | [`04-cylab-heap-3`](04-cylab-heap-3) | Core | 35 min | Exploit a use-after-free bug via allocator (tcache) reuse. |
| 7 | [`bonus-cylab-heap-havoc`](bonus-cylab-heap-havoc) | Bonus | 40 min | Overflow one heap struct into the next to reach a hidden function pointer field. |
| 8 | [`bonus-heap-mayhem`](bonus-heap-mayhem) | Bonus | 50 min | Combine an information leak with a heap overflow to defeat ASLR and hijack control flow in a PIE binary. |

Reference solutions and exploit scripts for every task are available in [`solutions/`](solutions).
</content>
