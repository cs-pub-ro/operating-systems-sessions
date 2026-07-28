# Copy File — malloc Variant

## Aim

Implement a file-copy program that allocates a **heap buffer** with `malloc()`
and uses `memcpy()` to transfer data from a source file to a destination file.

This exercise illustrates:
1. How to request and release heap memory at runtime with `malloc()` / `free()`.
2. The importance of freeing every allocation to avoid **memory leaks**.
3. How `memcpy()` copies data between two heap regions.

## Background

### Heap memory — malloc and free

```c
void *malloc(size_t size);
void  free(void *ptr);
```

`malloc(size)` asks the C runtime (and ultimately the OS) for `size` bytes of
memory.  It returns a pointer to the first byte, or `NULL` if the allocation
fails.  The memory persists until you call `free(ptr)` — it is **not** released
automatically when a variable goes out of scope.

Forgetting to call `free()` is a *memory leak*: the process consumes more and
more memory over time.  Tools like `valgrind` and AddressSanitizer (`-fsanitize=address`)
can detect leaks.

### memcpy

```c
void *memcpy(void *dest, const void *src, size_t n);
```

Copies exactly `n` bytes from `src` to `dest`.  The two regions **must not
overlap**.

## Tasks

Open `copy_file.c` and complete the following TODOs:

### TODO 1 — Allocate the read buffer

```c
char *buffer = malloc(BUFFER_SIZE);
if (!buffer) {
    perror("malloc");
    return EXIT_FAILURE;
}
```

### TODO 2, 3, 6 — Free on early exit paths

Every early-return path must call `free(buffer)` before returning, otherwise
the allocation leaks:

```c
free(buffer);
return EXIT_FAILURE;
```

### TODO 4 — Allocate a per-chunk write buffer and memcpy

Inside the read loop, allocate a temporary buffer and copy the data:

```c
char *write_buf = malloc(bytes_read);
if (!write_buf) {
    perror("malloc write_buf");
    fclose(src);
    fclose(dst);
    free(buffer);
    return EXIT_FAILURE;
}
memcpy(write_buf, buffer, bytes_read);
```

### TODO 5 — Write and free the per-chunk buffer

```c
size_t bytes_written = fwrite(write_buf, 1, bytes_read, dst);
free(write_buf);
if (bytes_written != bytes_read) {
    fprintf(stderr, "fwrite: short write\n");
    fclose(src);
    fclose(dst);
    free(buffer);
    return EXIT_FAILURE;
}
```

### TODO 7 — Free the read buffer on success

```c
free(buffer);
```

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

## Check for memory leaks (optional)

```bash
valgrind --leak-check=full ./copy_file input.bin output.bin
```

## Clean

```bash
make clean
```
