# Copy File — mmap Variant

## Aim

Implement a file-copy program that uses `mmap()` to map both the source and the destination files into the process address space, then copies their contents with a single `memcpy()` call.

This exercise illustrates:

1. How `mmap()` maps a file (or anonymous memory) into virtual address space.
1. How the kernel transparently handles I/O through page faults when you read/write mapped regions.
1. How `munmap()` releases a mapping, and how `msync()` flushes dirty pages back to the file.

## Background

### mmap — mapping files into memory

```c
void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
```

| Parameter | Meaning |
|-----------|---------|
| `addr`    | Preferred start address; pass `NULL` to let the kernel decide. |
| `length`  | Number of bytes to map. |
| `prot`    | Protection: `PROT_READ`, `PROT_WRITE`, `PROT_READ\|PROT_WRITE`. |
| `flags`   | `MAP_PRIVATE` — copy-on-write (changes do not affect the file). `MAP_SHARED` — changes are written back to the file. |
| `fd`      | File descriptor of the file to map. |
| `offset`  | Offset within the file (must be page-aligned; use `0` to start from the beginning). |

Returns a pointer to the mapped region, or `MAP_FAILED` on error.

After a successful `mmap()` the file descriptor can be closed — the mapping keeps the file referenced internally until `munmap()` is called.

### ftruncate — setting file size

```c
int ftruncate(int fd, off_t length);
```

Before mapping a destination file for writing it must be at least `length` bytes long.
`ftruncate()` extends (or shrinks) the file to exactly `length` bytes, filling new space with zeros.

### munmap and msync

```c
int munmap(void *addr, size_t length);
int msync(void *addr, size_t length, int flags);
```

`munmap()` releases the mapping.
For `MAP_SHARED` mappings, use `msync(addr, length, MS_SYNC)` before `munmap()` to guarantee dirty pages are flushed to disk.

## Tasks

Open `copy_file.c` and complete the following TODOs:

### TODO 1 — Map the source file (read-only)

```c
void *src_map = mmap(NULL, file_size, PROT_READ, MAP_PRIVATE, src_fd, 0);
if (src_map == MAP_FAILED) {
    perror("mmap source");
    close(src_fd);
    return EXIT_FAILURE;
}
close(src_fd);  /* fd no longer needed after mmap */
```

`MAP_PRIVATE` is used because we only need to read the source; we do not want changes reflected back to the file.

### TODO 2 — Unmap src_map on early exit

Any error path after the source mapping is created must call `munmap(src_map, file_size)` before returning.

### TODO 3 — Resize the destination file with ftruncate

```c
if (ftruncate(dst_fd, (off_t)file_size) < 0) {
    perror("ftruncate");
    close(dst_fd);
    munmap(src_map, file_size);
    return EXIT_FAILURE;
}
```

Without this step `mmap()` on the destination would fail because the file is empty and cannot back a mapping of `file_size` bytes.

### TODO 4 — Map the destination file (read-write, shared)

```c
void *dst_map = mmap(NULL, file_size, PROT_READ | PROT_WRITE,
                     MAP_SHARED, dst_fd, 0);
if (dst_map == MAP_FAILED) {
    perror("mmap destination");
    close(dst_fd);
    munmap(src_map, file_size);
    return EXIT_FAILURE;
}
close(dst_fd);
```

`MAP_SHARED` means that writes to `dst_map` are eventually written back to the underlying file.

### TODO 5 — Copy with memcpy

```c
memcpy(dst_map, src_map, file_size);
```

Both `src_map` and `dst_map` are ordinary pointers to virtual memory.
`memcpy()` copies bytes between them; the kernel resolves page faults to load source pages and allocate destination pages as needed.

### TODO 6 — Flush and unmap

```c
msync(dst_map, file_size, MS_SYNC);   /* flush dirty pages to disk */
munmap(src_map, file_size);
munmap(dst_map, file_size);
```

## Build

```console
make
```

## Run

```console
./copy_file <source> <destination>
```

Example:

```console
dd if=/dev/urandom of=input.bin bs=1M count=4
./copy_file input.bin output.bin
diff input.bin output.bin && echo "Files are identical"
```

## Clean

```console
make clean
```
