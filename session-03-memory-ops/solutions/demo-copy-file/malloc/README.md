# Copy File — malloc Variant (Solution)

## Overview

This variant copies a file using a **heap-allocated buffer** obtained via
`malloc()`.  The buffer is allocated at runtime and must be explicitly freed
with `free()` when it is no longer needed.  `memcpy()` is used to move data
between the read buffer and a per-chunk write buffer.

Key learning points:
- `malloc(size)` allocates `size` bytes on the heap and returns a pointer.
- Every successful `malloc()` must be paired with a `free()` to avoid memory
  leaks.
- `memcpy(dst, src, n)` copies `n` bytes from `src` to `dst`; the regions
  must not overlap.

## Build

```bash
make
```

## Run

```bash
./copy_file <source> <destination>
```

Example:

```bash
dd if=/dev/urandom of=input.bin bs=1M count=4
./copy_file input.bin output.bin
diff input.bin output.bin && echo "Files are identical"
```

## Clean

```bash
make clean
```
