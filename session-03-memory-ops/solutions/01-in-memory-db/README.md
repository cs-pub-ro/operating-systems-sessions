# Solution: a growable in-memory database

This is the reference implementation of the growable in-memory database exercise in [`01-in-memory-db`](../../01-in-memory-db).

## What it is

A tiny database that lives entirely on the heap.
Records are read from standard input into a dynamically allocated array that **grows in chunks of `CHUNK` records** whenever it fills up, and is printed back out at the end.

The three functions you had to write are:

* `db_init()` — start empty: `records = NULL`, `count = 0`, `capacity = 0`.
* `db_add()` — grow with `realloc` when `count == capacity`, then store the record at index `count` and increment it.
  Because `realloc(NULL, size)` behaves exactly like `malloc(size)`, the same "grow when full" branch handles the very first allocation too — there is no special case for the empty database.
* `db_free()` — release the array and reset the fields.

Files:

* `main.c` — the completed implementation.
* `input.txt` — sample records to feed on standard input.

## Build and run

```console
make
./db < input.txt
```

```text
Database holds 10 record(s) (capacity 12):
  [1] alice
  [2] bob
  [3] carol
  [4] dave
  [5] erin
  [6] frank
  [7] grace
  [8] heidi
  [9] ivan
  [10] judy
```

Ten records needed three reallocations: the capacity went `0 -> 4 -> 8 -> 12`, growing only on the arrival of the 1st, 5th and 9th record.
Feed it fewer records and watch the final capacity round up to the next multiple of `CHUNK`.

## Check for leaks

```console
valgrind --leak-check=full ./db < input.txt
```

Reports **0 errors** and **all heap blocks freed**.
