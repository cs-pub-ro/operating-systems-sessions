# heap0

**heap0** is a heap-exploitation CTF challenge. The goal is to corrupt a
"safe" heap variable that the player is never supposed to be able to
reach, by overflowing an adjacent, player-writable heap buffer.

## Requirements

The only requirement to build, publish, deploy, and solve this challenge
is **Docker**. No compiler, Python, or pwntools install is required on the
host machine.

## The bug

`init()` allocates two adjacent 5-byte buffers on the heap:

```c
input_data = malloc(INPUT_DATA_SIZE);   /* "pico" */
safe_var   = malloc(SAFE_VAR_SIZE);     /* "bico" */
```

`write_buffer()` copies player input into `input_data` with
`scanf("%s", input_data)` -- which has **no length limit**. glibc's
`malloc` rounds a 5-byte request up to a minimum usable chunk size (24
bytes on a 64-bit build), so writing more than that many bytes overflows
straight past `input_data`'s chunk and into whatever the allocator placed
right after it: `safe_var`.

The win condition is inverted on purpose:

```c
if (strcmp(safe_var, "bico") != 0) {
        /* print the flag */
}
```

`safe_var` starts out equal to `"bico"`; nothing in the program ever
changes it. The only way to win is to corrupt it into anything else.

## The exploit

Measured empirically (`1. Print Heap` shows both addresses; the delta
between them is the usable chunk size to overflow past):

```
input_data @ 0x...2b0
safe_var   @ 0x...2d0     (delta = 0x20 = 32 bytes)
```

So: write 32 filler bytes (to reach `safe_var`) followed by anything
non-empty, then check the win condition:

```python
payload = b"A" * 32 + b"XXXX"
```

See `solve/exploit.py` for the full script.

## Challenge structure

- **`build/`** -- source code and a reproducible Docker build environment.
  Produces `chall`, `libc.so.6`, and `ld-linux-x86-64.so.2`.
- **`publish/`** -- packages the binary and matching libc/loader into a
  zip archive for distribution to players.
- **`deploy/`** -- runs the vulnerable binary under `xinetd` inside a
  Docker container, exposed on a network port (default `31010`).
- **`solve/`** -- the exploit script (`exploit.py`) and a solver
  environment; runs locally, against a local deployment, or against a
  remote target.

## The flag

Stored in the `flag` file in this directory. During deployment it is
copied into the challenge container as `flag.txt`, alongside the binary
(the program does `fopen("flag.txt", "r")` using a path relative to its
own working directory).

## Getting started

Start with `build/README.md` to produce the binary, then follow
`publish/README.md`, `deploy/README.md`, and `solve/README.md` in order.
