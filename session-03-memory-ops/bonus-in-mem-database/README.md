# Bonus: a shrinking in-memory database

This exercise builds directly on [`01-in-memory-db`](../01-in-memory-db).
Start from **your finished `main.c`** of that task — copy it here — and extend it so the database can also **remove records** and **give memory back** when it no longer needs it.

If you have not finished the first task yet, do that first: this bonus assumes you already have working `db_init`, `db_add`, `db_print` and `db_free`, and that the array grows in chunks of `CHUNK` records (call it `N` from here on).

## The idea: grow *and* shrink

In the first task the capacity only ever went **up**, always a multiple of the chunk size `N`:

```text
capacity = 0, N, 2N, 3N, ...   (X * N for some X)
```

Now we make it symmetric.
When records are removed and the database becomes small enough to fit inside **one chunk less** than it currently owns, we shrink it back down.

Precisely: if the capacity is currently `X * N` and, after a removal, the number of records fits into `(X - 1) * N` (that is, `count <= (X - 1) * N`), then the array is **rearranged and reallocated down** to `(X - 1) * N` records.

```text
N = 4

capacity 8, count 5:  del one -> count 4 -> 4 <= 4 -> shrink to capacity 4
capacity 4, count 4:  del one -> count 3 -> 3 <= 0 ? no  -> stay at 4
capacity 4, count 1:  del one -> count 0 -> 0 <= 0 -> shrink to capacity 0 (free)
```

This is the exact mirror of the grow rule from task 1:

* **grow** when `count == capacity` (the array is full)   → `capacity + N`
* **shrink** when `count <= capacity - N` (a whole chunk is now unused) → `capacity - N`

Growing by `N` but only shrinking once a *full* chunk is free avoids "thrashing" — reallocating on every single add/remove around a boundary.

## What "rearranged" means

The records must stay **contiguous** at the front of the array, from index `0` to `count - 1`, with no holes.
When you remove a record from the middle you therefore have to close the gap before (or while) you shrink.
Two simple ways:

* **shift down:** move every record after the removed one one slot to the left (keeps the original order), or
* **swap with last:** copy the last record into the freed slot (does not keep order, but is cheaper).

Either is acceptable — pick one and be consistent.

## Your tasks

Working from your task-1 `main.c`:

1. **`db_remove(struct database *db, int id)`**
   * find the record whose `id` matches (linear scan is fine);
   * if none matches, do nothing and report it (return, e.g., `-1`);
   * otherwise **rearrange** the array so the remaining records stay contiguous, and decrement `count`.

1. **Shrink logic** (inside `db_remove`, after `count` was decreased)
   * if `capacity >= N` and `count <= capacity - N`, compute the new capacity `capacity - N` and `realloc` the array down to it;
   * handle the `new capacity == 0` case: `realloc(ptr, 0)` is implementation-defined, so free the array and set `records = NULL`, `capacity = 0` explicitly instead;
   * keep the invariant `count <= capacity` true at every step.

   > **Note:** shrinking `realloc` normally succeeds, but the standard still allows it to return `NULL`.
   > If it does, keep the old, larger buffer — the data is still valid there — and simply skip the shrink.

1. **Drive it from stdin.** Replace the input loop in `main` so each line is a command:

   ```text
   add <id> <name>     add a record   (as before)
   del <id>            remove a record by id
   ```

Read commands until end-of-file (Ctrl-D), then `db_print` and `db_free` as before.
You can copy this loop straight into your `main` — it reads the first word and dispatches to `db_add` / `db_remove`:

   ```c
   char cmd[16];
   int id;
   char name[NAME_LEN];

   while (scanf("%15s", cmd) == 1) {
   	if (strcmp(cmd, "add") == 0) {
   		if (scanf("%d %31s", &id, name) != 2)
   			break;
   		db_add(&db, id, name);
   	} else if (strcmp(cmd, "del") == 0) {
   		if (scanf("%d", &id) != 1)
   			break;
   		db_remove(&db, id);
   	} else {
   		fprintf(stderr, "unknown command: %s\n", cmd);
   	}
   }
   ```

(Remember to `#include <string.h>` for `strcmp`.)

## Build

```console
gcc -Wall -Wextra -o db main.c
```

## Run

```console
printf 'add 1 alice\nadd 2 bob\nadd 3 carol\nadd 4 dave\nadd 5 erin\ndel 5\ndel 4\n' | ./db
```

With `N == 4`, adding 5 records grows capacity to 8; deleting down to 3 records lets it fit in `1 * N`, so it shrinks back to 4:

```text
Database holds 3 record(s) (capacity 4):
  [1] alice
  [2] bob
  [3] carol
```

(If you chose *swap with last*, the order of the remaining records may differ — that is expected.)

## Check your work

```console
valgrind --leak-check=full ./db < input.txt
```

A correct solution reports **0 errors** and **all heap blocks freed**, both after growing and after shrinking.
Try inputs that repeatedly cross a chunk boundary (add 5, del 1, add 1, del 1, ...) and confirm the capacity in the final line matches the grow/shrink rules above.
