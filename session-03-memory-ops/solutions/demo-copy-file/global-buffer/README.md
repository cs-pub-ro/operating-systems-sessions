# Copy File — Global Buffer Variant (Solution)

## Overview

This variant copies a file using a **static global buffer** of fixed size.
The buffer is allocated at program start (in the BSS / data segment) and reused
for every read/write iteration.  `memcpy()` is used to move data from the
read buffer into a local staging area before writing, demonstrating in-memory
copy operations.

Key learning points:
- Static (global) memory lives for the entire lifetime of the process.
- No explicit allocation or deallocation is needed.
- `memcpy()` copies a block of bytes from one address to another.

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
