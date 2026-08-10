# Exercise: the `getpid` system call

In the [write demo](../demo-write-syscall) you saw the three-layer pattern:

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
