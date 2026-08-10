# heap1

**heap1** is a heap-exploitation CTF challenge, and a variant of `heap0`: the goal is again to overflow a player-writable heap buffer into an adjacent "safe" variable, but this time the corrupted value has to become one *specific* string, not merely a different one.

## Requirements

The only requirement to build, publish, deploy, and solve this challenge is **Docker**.

## The bug

Identical layout to `heap0`: `init()` allocates two adjacent 5-byte buffers, `input_data` and `safe_var`, and `write_buffer()` copies player input into `input_data` via `scanf("%s", ...)` with no length limit -- writing more than the usable chunk size overflows into `safe_var`.

The difference is the win condition:

```c
if (!strcmp(safe_var, "pico")) {
        /* print the flag */
}
```

`safe_var` starts out equal to `"bico"`.
This time it is not enough to merely change it -- it has to read exactly `"pico"` afterwards.

## The exploit

Same overflow distance as `heap0` (32 bytes to reach the start of `safe_var`), but the payload's tail must be the exact string the check compares against:

```python
payload = b"A" * 32 + b"pico"
```

See `solve/exploit.py` for the full script.

## Challenge structure

* **`build/`** -- source code and a reproducible Docker build environment.
* **`publish/`** -- packages the binary and matching libc/loader for distribution.
* **`deploy/`** -- runs the binary under `xinetd` in a container, exposed on port `31011`.
* **`solve/`** -- `exploit.py` and a solver environment (local / local deployment / remote).

## The flag

Stored in the `flag` file in this directory; copied into the deployed container as `flag.txt` next to the binary.

## Getting started

Start with `build/README.md`, then `publish/README.md`, `deploy/README.md`, and `solve/README.md` in order.
