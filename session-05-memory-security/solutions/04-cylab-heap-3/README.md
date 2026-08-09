# heap3

**heap3** is a use-after-free CTF challenge: freeing an object does not
erase the program's only pointer to it, and nothing stops the player from
allocating fresh memory that lands in exactly the same spot.

## Requirements

The only requirement to build, publish, deploy, and solve this challenge
is **Docker**.

## The bug

```c
struct object {
        char a[10];
        char b[10];
        char c[10];
        char flag[5];
};

static struct object *x;

static void free_memory(void) { free(x); }   /* x is never set to NULL */
```

Every other operation on `x` (`print_heap()`, `check_win()`, the menu's
"print x->flag" option) keeps dereferencing `x` as if it still pointed to
live memory. `check_win()` wins as soon as `x->flag` reads `"pico"`.

`alloc_object()` lets the player allocate a fresh, arbitrarily sized chunk
and write an arbitrary string into it -- the resulting pointer is
discarded, but if the allocator hands back the *same memory* `x` still
refers to (which glibc's tcache does, for same-size allocations
immediately following a free), the write goes through `x` as well.

## The exploit

1. **Free `x`** (menu option 5) -- `x` becomes a dangling pointer, and the
   chunk it pointed to is now the head of glibc's tcache free list for its
   size class.
2. **Allocate a new object of the same size** (`sizeof(struct object)` ==
   `10+10+10+5` == 35 bytes) and write
   `a[10] + b[10] + c[10] + "pico"` into it. The tcache hands back exactly
   the chunk that used to be `x`.
3. **Check the win condition.** `x->flag` now reads `"pico"`, because `x`
   and the "new" allocation are the same memory.

See `solve/exploit.py` for the full script.

## Challenge structure

- **`build/`** -- source and a reproducible Docker build environment
  (`-no-pie`, matching the deployed binary's addressing).
- **`publish/`** -- packages the binary and matching libc/loader. Shipping
  the exact glibc used to build matters here: tcache reuse behaviour is an
  allocator implementation detail.
- **`deploy/`** -- runs the binary under `xinetd` in a container, exposed
  on port `31013`.
- **`solve/`** -- `exploit.py` and a solver environment.

## The flag

Stored in the `flag` file in this directory; copied into the deployed
container as `flag.txt` next to the binary.

## Getting started

Start with `build/README.md`, then `publish/README.md`,
`deploy/README.md`, and `solve/README.md` in order.
