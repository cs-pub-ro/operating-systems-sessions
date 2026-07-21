# Demo: the `write` system call

This is a **fully solved demo**. Read the code together with this README to
understand how a program talks to the kernel *directly*, without going through
the C standard library.

## What is a system call?

Your program runs in **user mode** and cannot touch hardware, files or other
processes on its own. Whenever it needs the operating system to do something
privileged (write to a file, allocate memory, create a process, ...) it asks
the kernel by performing a **system call**.

Normally you call a libc function such as `printf` or `write`, and libc issues
the system call for you. In this session we build those wrappers **ourselves**.

## The three layers

The demo is organised as three layers, each built on top of the previous one:

```
  my_puts()      <-- layer 3: a tiny "libc" helper (like puts)
     |
  my_write()     <-- layer 2: a typed wrapper for the write syscall
     |
  my_syscall()   <-- layer 1: the generic wrapper (issues `syscall`)
     |
  [ kernel ]
```

### Layer 1 — `my_syscall()` (in `main.c`)

The generic wrapper. On **x86-64 Linux** a system call works like this:

| Register | Meaning        |
|----------|----------------|
| `RAX`    | syscall number |
| `RDI`    | argument 1     |
| `RSI`    | argument 2     |
| `RDX`    | argument 3     |
| `R10`    | argument 4     |
| `R8`     | argument 5     |
| `R9`     | argument 6     |

We load these registers using inline assembly and execute the `syscall`
instruction. The kernel returns its result in `RAX`.

### Layer 2 — `my_write()` (in `main.c`)

`write(2)` has the prototype:

```c
ssize_t write(int fd, const void *buf, size_t count);
```

Its syscall number on x86-64 is **1**. `my_write()` just forwards `fd`, `buf`
and `count` to `my_syscall()`.

### Layer 3 — `my_puts()` (in `main.c`)

A convenience function like `puts`: it measures the string length by hand and
calls `my_write()` to print the text plus a newline to `STDOUT_FILENO` (fd 1).

## Build

No Makefile. Just compile the single source file:

```sh
gcc -Wall -Wextra -o demo main.c
```

## Run

```sh
./demo
```

Expected output:

```
Hello from a raw write(2) system call!
No printf, no libc puts -- just my_syscall().
```

## Verify it really uses the syscall

Trace the system calls the program makes:

```sh
strace ./demo
```

You should see `write(1, "Hello from a raw write(2) system"..., 38) = 38`
lines — proof that our wrapper reached the kernel.

> **Note:** the inline assembly is specific to **x86-64 Linux**. The syscall
> numbers and calling convention are different on other architectures.
