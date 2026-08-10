A seemingly harmless program takes two names as arguments, but there's a catch.
Overflowing one name on the heap can reach into the *other* name's struct -- and one of its fields is a function pointer nobody ever checks before calling.

Link: https://learn.cylabacademy.org/library/763

## Files

* `chall.c` -- the challenge source code.
* `chall` -- the compiled challenge binary (32-bit).
  Run it locally with `./chall <name1> <name2>` (it looks for `flag.txt` in the current directory).

## Hints

1. Pay attention to how the program allocates your input on the heap, and in what order the two allocations happen relative to each other.
1. `objdump -d` can help you find the address of the hidden function that is never called from anywhere in the visible control flow.
1. Reflect on how overwriting a function pointer field -- not a return address -- could redirect program execution to that hidden functionality.
1. The struct that gets overflowed into has more than one field between the start of the overflow and the field you actually want to hit.
