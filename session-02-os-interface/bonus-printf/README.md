# Bonus Exercise: plugging `_putchar()` into a custom `printf`

## Overview

The [`printf/`](../printf/) directory contains a self-contained, portable `printf` implementation ([mpaland/printf](https://github.com/mpaland/printf)).
Unlike the standard libc `printf`, it does **not** know how to write to the terminal by itself.
Instead it delegates every output character to a single hook that *you* must provide:

```c
void _putchar(char character);
```

Your task is to implement this hook so that the custom `printf` writes to **standard output** using the `write(2)` system call — exactly the same system call you explored in the demos and earlier exercises.

The layering looks like this:

```text
printf() / sprintf() / ...
        |
        v
   _putchar(c)          <-- you implement this
        |
        v
  write(1, &c, 1)       <-- write syscall, fd 1 = stdout
        |
        v
      kernel
```

## Your task

Open `_putchar.c` and fill in the TODO:

```c
void _putchar(char character)
{
    /* TODO: call write() to output `character` to stdout (fd 1). */
}
```

`write(2)` signature (from `<unistd.h>`):

```c
ssize_t write(int fd, const void *buf, size_t count);
```

* `fd` — file descriptor; use **1** for stdout.
* `buf` — pointer to the data to write; pass the address of `character`.
* `count` — number of bytes; always **1** here.

## Build

```console
make
```

## Run

```console
./printfdemo
```

Expected output:

```text
Hello, World!
Decimal:     42
Negative:    -7
Hex:         0xdeadbeef
Octal:       0755
Padded:              42
Left-align:  42        |
Zero-pad:    00000042
String:      operating systems
Char:        A
Float:       3.1416
```

## Check your work

Confirm that `write` is the only output syscall being used:

```console
strace -e trace=write ./printfdemo
```

Every line of output should correspond to individual `write(1, ...)` calls, one per character — there should be no `fwrite`, `puts`, or libc `printf` calls at all.

> **Note:** the `printf/` library also provides `sprintf()`, `snprintf()`, `fprintf()`, and more.
> Once `_putchar()` works you can experiment with those too.
