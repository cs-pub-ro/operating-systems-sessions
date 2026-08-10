# Copy String Tutorial

## Overview

This tutorial demonstrates how different approaches to string concatenation in C can yield significantly different performance outcomes.

Two programs build the same string (`"John, Paul, George, Joel "`) 100,000,000 times and measure the elapsed time:

* **`copy-string`** — uses `strcat` repeatedly, which must scan to the end of the string on every call.
* **`copy-string-improved`** — uses `strcpy` with precomputed offsets, writing each fragment directly to the correct position without re-scanning.

The goal is to illustrate that even simple-looking standard library calls can have hidden algorithmic costs, and that understanding what a function does internally allows you to write measurably faster code.

## Building

```console
make
```

This produces two executables: `copy-string` and `copy-string-improved`.

To clean up:

```console
make clean
```

## Running

```console
./copy-string
./copy-string-improved
```

Each program prints the elapsed time in microseconds, for example:

```text
time passed 3241847 microseconds
time passed 891203 microseconds
```

## Explanation of Results

### `copy-string` (slow)

```c
bigString[0] = '\0';
strcat(bigString, "John, ");
strcat(bigString, "Paul, ");
strcat(bigString, "George, ");
strcat(bigString, "Joel ");
```

`strcat(dst, src)` first walks `dst` from the beginning to find its null terminator, then copies `src` there.
With four consecutive `strcat` calls:

* The 1st call scans 0 characters before appending.
* The 2nd call scans 6 characters (`"John, "`).
* The 3rd call scans 12 characters (`"John, Paul, "`).
* The 4th call scans 21 characters (`"John, Paul, George, "`).

This redundant scanning grows with the number of fragments and repeats on every one of the 100,000,000 iterations.

### `copy-string-improved` (fast)

```c
strcpy(bigString,                                            "John, ");
strcpy(bigString + strlen("John, "),                         "Paul, ");
strcpy(bigString + strlen("John, ") + strlen("Paul, "),      "George, ");
strcpy(bigString + strlen("John, ") + strlen("Paul, ") + strlen("George, "), "Joel ");
```

`strcpy` simply copies bytes from source to destination without scanning the destination first.
By computing the target offset once per call (using compile-time-constant `strlen` values), each fragment is written directly to its final position — no wasted scanning.

### Why the difference matters

`strcat` is O(n) in the current length of the destination string.
When called k times to build a string of total length L, the total work is O(L·k) per iteration.

`strcpy` with explicit offsets is O(1) per fragment (proportional only to the fragment length), giving O(L) per iteration — a constant-factor improvement that becomes very visible at 10⁸ iterations.
