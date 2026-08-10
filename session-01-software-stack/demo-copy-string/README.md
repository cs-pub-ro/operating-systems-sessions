# Copy String Demo

## Overview

This demo shows how different approaches to string concatenation in C can yield significantly different performance outcomes.

We will create two programs the build the same string (`"John, Paul, George, Joel "`) 100,000,000 times and measure the elapsed time:

* **`copy-string`** — we use `strcat` repeatedly, which must scan to the end of the string on every call.
* **`copy-string-improved`** — will use `strcpy` with precomputed offsets, writing each fragment directly to the correct position without re-scanning.

The goal is to illustrate that even simple-looking standard library calls can have hidden algorithmic costs, and that understanding what a function does internally allows you to write measurably faster code.

## Implement

We will fill the TODO areas in `copy-string.c` and `copy-string-improved.c` with the corresponding `strcat()` and `strcpy()` calls, respectively.

## Build

To build the corresponding two binary executables, we use:

```console
make
```

This produces two binary executables: `copy-string` and `copy-string-improved`.

## Run

Run the resulting two executables:

```console
./copy-string
./copy-string-improved
```

Each program prints the elapsed time in microseconds, for example:

```text
time passed 3241847 microseconds
time passed 891203 microseconds
```

Discuss results with the lab assistant.
