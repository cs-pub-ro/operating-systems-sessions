# Exercise: the `getpid` system call

In the [write demo](../../demo-puts-write) you saw the three-layer pattern:

```text
  high-level helper   -->   syscall wrapper   -->   my_syscall()   -->   kernel
```

Now you build the same thing for **`getpid(2)`**, the system call that returns the Process ID of the calling process.

## Your tasks

Open `main.c` and complete the two TODOs:

1. **`SYS_getpid`** — define the correct x86-64 syscall number for `getpid`.
1. **`my_getpid()`** — the syscall wrapper.
   `getpid` takes no arguments and returns the PID.
   Call `my_syscall()` with the getpid number and `0` for every argument, and return its result.

### Finding the syscall number

```console
less /usr/include/asm/unistd_64.h
```

`getpid` is one of the simplest system calls: no arguments, just a return value.

## Build

```console
gcc -Wall -Wextra -o getpid main.c
```

## Run

```console
./getpid
```

Expected output (your number will differ):

```text
PID: 12345
```

## Check your work

Confirm the number you print matches the one the kernel reports:

```console
strace -e trace=getpid ./getpid
```

You should see a `getpid()` line whose return value equals the PID you printed.

> **Hint:** run `./getpid` twice — the PID changes every run, because each run is a new process.

## Solution

### `SYS_getpid`

The x86-64 syscall number for `getpid` is **39**.

Note that the number is architecture-specific: the same call is 20 on 32-bit x86 and 172 on AArch64. This is why the table lives in an `asm/` header. On Debian and Ubuntu the file is at a multiarch path:

```console
grep '__NR_getpid ' /usr/include/x86_64-linux-gnu/asm/unistd_64.h
```

### `my_getpid()`

`getpid` is the simplest possible system call: no arguments, no output parameters, no error cases. Every argument slot is 0, and the kernel's return value in `%rax` is the PID:

```c
long my_getpid(void)
{
    return my_syscall(SYS_getpid, 0, 0, 0, 0, 0, 0);
}
```

There is nothing between this and the kernel — no libc, no buffering, no caching.

### Checking it

```console
$ strace -e trace=getpid ./getpid
getpid()                                = 248529
PID: 248529
+++ exited with 0 +++
```

The kernel reports the same number the program prints, which is the proof that the PID really came from the syscall rather than from somewhere else.

> **Worth knowing:** glibc's `getpid()` used to cache the result in userspace to avoid the syscall, which caused long-standing bugs around `fork()` and `clone()`. The cache was removed in glibc 2.25, so a modern `getpid()` really does enter the kernel every time — just like this one.
