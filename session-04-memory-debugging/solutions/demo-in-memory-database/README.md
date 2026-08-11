# Solution: the demo in-memory database

This is the repaired version of the database used in the gdb-and-Valgrind demo in [`demo-in-memory-database`](../../demo-in-memory-database).

## The three fixes

Each one is marked with a `FIX n` comment in `main.c`.

**FIX 1 — `db_add()`: the grow condition underflowed on an empty database.**
The buggy version tested `count == capacity - 1`.
Both fields are `size_t`, so on an empty database `capacity - 1` did not become `-1` — it wrapped around to `SIZE_MAX`.
The test was false, the array was never allocated, and the store below it dereferenced `NULL`.
The array is full exactly when `count == capacity` — say that, and the empty case takes care of itself.
Found with gdb: the segfault, then `print db` at the top of the frame.

**FIX 2 — `main()`: a cached record pointer survived a `realloc()`.**
`main()` kept a `struct record *` to the first record and read through it after more records had been added.
`realloc()` is free to move the block, which leaves every pointer into the old one dangling.
Either copy the data out, or remember the **index** and re-derive the pointer through the current `db.records` each time.
Found with gdb (the mechanism) and Valgrind (the timeline: allocated here, freed there, read afterwards).

**FIX 3 — `db_print_sorted()`: the temporary sorted copy was never freed.**
The function allocates a private scratch array, sorts it, prints it and returns — 360 bytes definitely lost, and nothing at all visible in the output.
This is the class of bug gdb cannot help with: there is no crash to break on and no wrong value to print.
Whoever allocates a scratch buffer frees it on **every** exit path, error branches included.

Files:

* `main.c` — the fixed implementation.
* `input.txt` — the sample records.

## Build and run

```console
make
valgrind --leak-check=full ./db < input.txt
```

```text
==2741272== HEAP SUMMARY:
==2741272==     in use at exit: 0 bytes in 0 blocks
==2741272==   total heap usage: 6 allocs, 6 frees, 9,416 bytes allocated
==2741272==
==2741272== All heap blocks were freed -- no leaks are possible
==2741272==
==2741272== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

**"All heap blocks were freed"** plus **"0 errors from 0 contexts"** is the result to aim for in every assignment from now on.
