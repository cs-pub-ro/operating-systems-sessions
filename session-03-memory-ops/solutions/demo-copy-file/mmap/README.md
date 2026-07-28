# Copy File — mmap Variant (Solution)

## Overview

This variant copies a file by **memory-mapping** both the source and the
destination with `mmap()`, then using a single `memcpy()` to transfer the
data.  The kernel handles all the actual I/O behind the scenes through its
page-cache mechanism.

Key learning points:
- `mmap(NULL, size, prot, flags, fd, 0)` maps a file (or anonymous memory)
  into the process address space and returns a pointer.
- The mapped region behaves like ordinary memory; reads and writes translate
  to page faults that the kernel resolves by loading/storing file pages.
- `munmap(addr, size)` releases the mapping.
- `msync(addr, size, MS_SYNC)` ensures dirty pages are written back to the
  underlying file before the mapping is released.

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
