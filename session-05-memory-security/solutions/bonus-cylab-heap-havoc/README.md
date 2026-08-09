# heap-havoc

**heap-havoc** is a bonus heap-exploitation challenge: two command-line
arguments get copied, unchecked, into two adjacent heap structs, each of
which holds a function pointer that main() calls if it is non-NULL.

## Requirements

The only requirement to build, publish, deploy, and solve this challenge
is **Docker** (including for the 32-bit compiler toolchain needed to build
this binary -- the Dockerfile installs `gcc-multilib`, so no host-side
32-bit dev environment is required).

## The bug

```c
struct internet {
        int priority;
        char *name;
        void (*callback)(void);
};

i1 = malloc(sizeof(*i1));
i1->name = malloc(8);
i1->callback = NULL;

i2 = malloc(sizeof(*i2));
i2->name = malloc(8);
i2->callback = NULL;

strcpy(i1->name, argv[1]);   /* no bounds check */
strcpy(i2->name, argv[2]);   /* no bounds check */

if (i1->callback) i1->callback();
if (i2->callback) i2->callback();
```

`i1->name` and `i2->name` are both 8-byte allocations. `i1`, `i1->name`,
`i2`, and `i2->name` are allocated back-to-back on the heap, in that
order, so `i1->name`'s chunk is immediately followed by `i2`'s struct.
Overflowing `argv[1]` past `i1->name`'s usable chunk size reaches straight
into `i2->priority`, `i2->name`, and `i2->callback` -- all three, in that
order, 4 bytes apiece (this is a 32-bit binary).

Nothing ever sets any `callback` to a non-NULL value except this overflow
-- and there is a function, `winner()`, that nothing in the visible
control flow ever calls.

## The exploit

Measured with gdb (breakpoint right after the four `malloc()` calls,
comparing `i2`'s address against `i1->name`'s address): `i2`'s struct
starts exactly **16 bytes** after the start of `i1->name`'s buffer.

So `argv[1]` is built as:

```
16 bytes filler          -- reaches the start of i2
 4 bytes filler           -- i2->priority, contents irrelevant
 4 bytes writable address -- i2->name (must be valid: main() does
                              strcpy(i2->name, argv[2]) *after* this
                              overflow already happened)
 4 bytes winner()'s address -- i2->callback
```

For `i2->name`'s overwritten value, any writable, always-mapped address
works -- this solution reuses the binary's own `.bss` section start
(`__bss_start`), since the binary is non-PIE and that address never
changes.

```python
payload = filler(16) + b"B"*4 + p32(bss_addr) + p32(winner_addr)
```

`argv[2]` just needs to be short; it gets written to whatever address we
put in `i2->name`.

### Delivering argv over the network

This challenge takes its input as `argv[1]`/`argv[2]`, which a bare TCP
socket cannot carry directly. The deployed `wrapper.sh` reads two lines
from the connection and re-execs the binary with them as its two
arguments -- so the remote exploit sends two lines instead of using
`process([..., arg1, arg2])`.

See `solve/exploit.py` for the full script.

## Challenge structure

- **`build/`** -- source and a Docker build environment with
  `gcc-multilib` (builds a 32-bit, non-PIE binary).
- **`publish/`** -- packages the binary and matching 32-bit libc/loader.
- **`deploy/`** -- runs the binary under `xinetd` in a container. The
  wrapper script reads two newline-terminated names from the connection
  and re-execs the binary with them as argv. Exposed on port `31020`.
- **`solve/`** -- `exploit.py`, which builds the payload from the ELF's
  own symbol table (`winner`, `.bss`) and either runs the binary directly
  with argv (local) or speaks the two-line protocol (remote).

## The flag

Stored in the `flag` file in this directory; copied into the deployed
container as `flag.txt` next to the binary.

## Getting started

Start with `build/README.md`, then `publish/README.md`,
`deploy/README.md`, and `solve/README.md` in order.
