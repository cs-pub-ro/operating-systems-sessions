# Bonus Exercise: `clock_gettime` and `time`

Same three-layer pattern as the previous exercises:

```
  my_time()   -->   my_clock_gettime()   -->   my_syscall()   -->   kernel
```

This time you implement **`clock_gettime(2)`**, the system call that reads a
high-resolution clock, and build a libc-style **`time()`** on top of it.

## Background: `clock_gettime` and `struct timespec`

`clock_gettime` returns the time for a specified clock as a `timespec` (run
`man 2 clock_gettime`):

```c
struct timespec {
    time_t tv_sec;   /* whole seconds        */
    long   tv_nsec;  /* nanoseconds [0, 1e9) */
};
```

Its prototype is:

```c
int clock_gettime(clockid_t clkid, struct timespec *tp);
```

- `clkid` — which clock to read, e.g. `CLOCK_REALTIME` (wall-clock time since
  the Unix Epoch) or `CLOCK_MONOTONIC` (monotonically increasing, good for
  measuring durations).
- `tp` — output parameter; the kernel fills it with the current time.

`time(2)` is a simpler call that returns only the whole-second part of
`CLOCK_REALTIME`:

```c
time_t time(time_t *tloc);
```

It can be implemented on top of `clock_gettime` by reading `CLOCK_REALTIME`
and returning `tv_sec`.

## Your tasks

### 1. `my_time.h` — declare the two functions

Open `my_time.h` and add the function declarations for `my_clock_gettime()`
and `my_time()` where the TODO comments indicate.

### 2. `my_time.c` — implement the functions

Open `my_time.c` and complete the three TODOs:

1. **`SYS_clock_gettime`** — define the correct x86-64 syscall number.
2. **`my_clock_gettime()`** — the syscall wrapper. Pass `clkid` as the first
   argument and `tp` (cast to `long`) as the second; use `0` for the rest.
3. **`my_time()`** — get `CLOCK_REALTIME` via `my_clock_gettime()`, optionally
   write the result to `*tloc`, and return `tv_sec`.

### Finding the syscall number

```sh
less /usr/include/asm/unistd_64.h
```

## Build

```sh
make
```

## Run

```sh
./clock_gettime_demo
```

Expected output (numbers will differ):

```
my_clock_gettime: tv_sec=1753000000, tv_nsec=123456789
my_time:          1753000000
```

The two `tv_sec` / `my_time` values should be equal (or differ by at most 1).

## Check your work

Verify the syscall is actually invoked:

```sh
strace -e trace=clock_gettime ./clock_gettime_demo
```

You should see two `clock_gettime(CLOCK_REALTIME, ...)` lines (one per
function call in `main`), and the kernel-reported seconds should match what
you printed.

You can also cross-check against the system's `date` command:

```sh
date +%s
```

## Solution

### `SYS_clock_gettime`

The x86-64 syscall number for `clock_gettime` is **228**. You can verify this
with:

```sh
grep clock_gettime /usr/include/asm/unistd_64.h
```

### `my_clock_gettime()`

`clock_gettime` takes two arguments: the clock ID (an integer) and a pointer
to a `struct timespec`. We pass them as the first two arguments to
`my_syscall()`, casting the pointer to `long` as the calling convention
requires:

```c
int my_clock_gettime(clockid_t clkid, struct timespec *tp)
{
    return (int)my_syscall(SYS_clock_gettime, (long)clkid, (long)tp,
                           0, 0, 0, 0);
}
```

### `my_time()`

`time()` only needs whole seconds. We read `CLOCK_REALTIME` via
`my_clock_gettime()` and extract `tv_sec`. If the caller passed a non-NULL
`tloc`, we store the result there before returning it:

```c
time_t my_time(time_t *tloc)
{
    struct timespec ts;

    my_clock_gettime(CLOCK_REALTIME, &ts);
    if (tloc != NULL)
        *tloc = ts.tv_sec;
    return ts.tv_sec;
}
```

This mirrors exactly how glibc implements `time()` internally — it is just a
thin wrapper around `clock_gettime(CLOCK_REALTIME, ...)`.
