# heap2

**heap2** is a heap-exploitation CTF challenge built around a function pointer that is not what it appears to be: `check_win()` does not compare anything -- it dereferences a heap buffer as a function pointer and calls it.
Whatever bytes are sitting in that buffer decide what runs.

## Requirements

The only requirement to build, publish, deploy, and solve this challenge is **Docker**.

## The bug

```c
void check_win(void)
{
        ((void (*)(void))*(int *)x)();
}
```

`x` is a 5-byte heap allocation.
This line reads a 4-byte value out of the memory `x` points to, and calls it as a function with no arguments.
`x` itself starts out holding the string `"bico"` -- interpreted as function-pointer bytes, that is garbage, so calling `check_win()` unmodified just crashes (or does nothing useful).

`x` sits right after another 5-byte allocation, `input_data`, which the player can write to via `write_buffer()`'s unbounded `scanf("%s", input_data)`.
Overflowing `input_data` reaches into `x`'s buffer -- and whatever 4 (or 8) bytes end up there is what gets called.

## The exploit

Same 32-byte overflow distance as `heap0`/`heap1` to reach the target buffer, followed by the address of `win()` (the hidden function that prints the flag), packed little-endian to match x86-64 byte order:

```python
payload = b"A" * 32 + p64(win_addr)
```

`win_addr` is read directly out of the public binary's symbol table (`ELF("chall").symbols["win"]`) -- this binary is built **without** PIE, so that address is a fixed, load-time-independent constant.

See `solve/exploit.py` for the full script.

## Challenge structure

* **`build/`** -- source and a reproducible Docker build environment (`-no-pie`, so `win()`'s address never changes between runs).
* **`publish/`** -- packages the binary and matching libc/loader.
* **`deploy/`** -- runs the binary under `xinetd` in a container, exposed on port `31012`.
* **`solve/`** -- `exploit.py` and a solver environment.
  Needs the binary mounted even for remote solving, since it reads `win()`'s address out of the ELF symbol table.

## The flag

Stored in the `flag` file in this directory; copied into the deployed container as `flag.txt` next to the binary.

## Getting started

Start with `build/README.md`, then `publish/README.md`, `deploy/README.md`, and `solve/README.md` in order.
