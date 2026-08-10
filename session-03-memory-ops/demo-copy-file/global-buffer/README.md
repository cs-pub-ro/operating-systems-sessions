# Copy File — Global Buffer Variant

## Aim

Implement a file-copy program that uses a **static global buffer** and `memcpy()` to transfer data from a source file to a destination file.

This exercise illustrates:

1. How static (global) memory is allocated at compile time and lives for the entire process lifetime.
1. How `memcpy()` copies a block of bytes between two memory regions.
1. The read → copy → write loop that underpins most simple I/O programs.

## Background

### Static global memory

When you declare a variable outside any function:

```c
static char buffer[1024 * 1024];
```

the compiler places it in the **BSS segment** (zero-initialised) or the **data segment** (if explicitly initialised).
The operating system maps this region into the process address space before `main()` is called.
You do not need `malloc()` or `free()` — the memory is always there.

### memcpy

```c
void *memcpy(void *dest, const void *src, size_t n);
```

Copies exactly `n` bytes from `src` to `dest`.
The two regions **must not overlap** (use `memmove()` if they might).

## Tasks

Open `copy_file.c` and complete the following TODOs:

### TODO 1 — Declare the global buffer

Add the following line at file scope (outside `main`):

```c
static char buffer[BUFFER_SIZE];
```

Because it is `static` and global, the buffer is zero-initialised and does not need to be freed.

### TODO 2 — Copy data with memcpy

Inside the read loop, after `fread()` fills `buffer`, declare a local staging array and copy the data into it:

```c
char local[BUFFER_SIZE];
memcpy(local, buffer, bytes_read);
```

This makes the use of `memcpy()` explicit.
In a real program you would write directly from `buffer`, but copying first is intentional here.

### TODO 3 — Write data to the destination file

Use `fwrite()` to write `bytes_read` bytes from `local` to `dst`, and check for a short write:

```c
size_t bytes_written = fwrite(local, 1, bytes_read, dst);
if (bytes_written != bytes_read) {
    fprintf(stderr, "fwrite: short write\n");
    fclose(src);
    fclose(dst);
    return EXIT_FAILURE;
}
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
