# Exercise: the `nanosleep` system call

Same three-layer pattern as the [write demo](../demo-puts-write) and the [getpid exercise](../01-getpid):

```text
  my_sleep()   -->   my_nanosleep()   -->   my_syscall()   -->   kernel
```

This time you implement **`nanosleep(2)`**, the system call that suspends the process for a given amount of time, and build a libc-style `sleep()` on top of it.

## Background: `struct timespec`

`nanosleep` describes durations with a `timespec` (run `man 2 nanosleep`):

```c
struct timespec {
    time_t tv_sec;   /* whole seconds        */
    long   tv_nsec;  /* nanoseconds [0, 1e9) */
};
```

To sleep for 2 seconds you fill `tv_sec = 2` and `tv_nsec = 0`.
To sleep for half a second you would use `tv_sec = 0`, `tv_nsec = 500000000`.

Its prototype is:

```c
int nanosleep(const struct timespec *req, struct timespec *rem);
```

* `req` — how long to sleep.
* `rem` — if the sleep is interrupted by a signal, the kernel writes the leftover time here.
  Pass `NULL` if you do not care.

## Your tasks

Open `main.c` and complete the three TODOs:

1. **`SYS_nanosleep`** — define the correct x86-64 syscall number.
1. **`my_nanosleep()`** — the syscall wrapper.
   Forward the two pointers (cast to `long`) to `my_syscall()`.
1. **`my_sleep()`** — build a `struct timespec` for the requested number of seconds and call `my_nanosleep()` with it (`rem = NULL`).

### Finding the syscall number

```console
less /usr/include/asm/unistd_64.h
```

## Build

```console
gcc -Wall -Wextra -o sleepdemo main.c
```

## Run

```console
./sleepdemo
```

Expected behaviour: it prints the first line, **pauses for about 2 seconds**, then prints the second line:

```text
Sleeping for 2 seconds...
Woke up!
```

## Check your work

Measure the elapsed time and inspect the syscall:

```console
time ./sleepdemo
strace -e trace=nanosleep ./sleepdemo
```

`time` should report roughly 2 seconds of real time, and `strace` should show a `nanosleep(...)` call with `tv_sec=2`.

> **Note:** a real `sleep()` would loop on `my_nanosleep()` and reuse the `rem` value to finish sleeping after a signal interruption.
> Handling that is an optional bonus.
