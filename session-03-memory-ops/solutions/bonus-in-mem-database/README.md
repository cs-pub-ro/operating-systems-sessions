# Solution: a shrinking in-memory database

This is the reference implementation of the bonus exercise in [`bonus-in-mem-database`](../../bonus-in-mem-database).

## What it is

The database from [`01-in-memory-db`](../01-in-memory-db) extended so it can also **remove records** and **give memory back**:

* **grow** when `count == capacity` (the array is full) → `capacity + N`
* **shrink** when `count <= capacity - N` (a whole chunk is now unused) → `capacity - N`

Growing by `N` but only shrinking once a *full* chunk is free avoids thrashing around a chunk boundary.
`db_remove()` closes the gap left by the removed record so the remaining ones stay contiguous at the front of the array, then applies the shrink rule.
When the new capacity would be `0` the array is freed outright and `records` set back to `NULL`, rather than relying on the implementation-defined behaviour of `realloc(ptr, 0)`.

Files:

* `main.c` — the completed implementation, with the `add` / `del` command loop.
* `input.txt` — sample commands to feed on standard input.

## Build and run

```console
make
printf 'add 1 alice\nadd 2 bob\nadd 3 carol\nadd 4 dave\nadd 5 erin\ndel 5\ndel 4\n' | ./db
```

With `N == 4`, adding 5 records grows the capacity to 8; deleting back down to 3 records lets them fit in `1 * N`, so the array shrinks to 4:

```text
Database holds 3 record(s) (capacity 4):
  [1] alice
  [2] bob
  [3] carol
```

## Check for leaks

```console
valgrind --leak-check=full ./db < input.txt
```

Reports **0 errors** and **all heap blocks freed**, both after growing and after shrinking.
