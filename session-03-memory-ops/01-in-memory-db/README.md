# Exercise: a growable in-memory database

In this exercise you build a tiny **in-memory database** that lives entirely on
the heap. Records are read from **standard input**, stored in a dynamically
allocated array, and printed back out at the end.

The interesting part is memory management: you never know in advance how many
records the user will type, so the array has to **grow on demand** using
`malloc`/`realloc`.

## The data model

A record is a single row with two fields:

```c
struct record {
	int id;
	char name[NAME_LEN];   /* NAME_LEN == 32 */
};
```

The database is just a heap array of records plus a bit of bookkeeping:

```c
struct database {
	struct record *records;   /* heap array of `capacity` records */
	size_t count;             /* records currently in use         */
	size_t capacity;          /* records the array can hold        */
};
```

The rule connecting the two counters is `count <= capacity`.

## How growth works

The array is grown in **constant chunks**, never one record at a time, and it
is **only ever expanded, never shrunk**:

```
CHUNK = 4

start:          records = NULL      count = 0   capacity = 0
add "1 alice":  need room -> grow   count = 0   capacity = 4    (realloc)
                store, count -> 1
add "2 bob":    room available      count = 2   capacity = 4
add "3 carol":                      count = 3   capacity = 4
add "4 dave":                       count = 4   capacity = 4
add "5 erin":   full -> grow        capacity = 8                (realloc)
                store, count -> 5
```

Because `realloc(NULL, size)` behaves exactly like `malloc(size)`, the *same*
"grow when full" code handles both the very first allocation and every later
expansion — you do not need a separate special case for the empty database.

## Your tasks

Open `main.c` and complete the three TODOs:

1. **`db_init()`** — start from an empty database: `records = NULL`,
   `count = 0`, `capacity = 0`.

2. **`db_add()`** — the heart of the exercise:
   - if `count == capacity`, grow the array by `CHUNK` records with `realloc`
     and check the result for `NULL`;
   - copy the `id` and `name` into the slot at index `count`
     (use `strncpy` and keep the string NUL-terminated);
   - increment `count`.

3. **`db_free()`** — `free` the array and reset the fields so the database is
   empty again.

`db_print()` and `main()` are already written for you.

## Build

```sh
gcc -Wall -Wextra -o db main.c
```

## Run

Type records and finish with **Ctrl-D**:

```sh
./db
1 alice
2 bob
3 carol
<Ctrl-D>
```

Expected output:

```
Database holds 3 record(s) (capacity 4):
  [1] alice
  [2] bob
  [3] carol
```

Or pipe input from a file / a here-string to force several reallocations:

```sh
printf '1 alice\n2 bob\n3 carol\n4 dave\n5 erin\n' | ./db
```

```
Database holds 5 record(s) (capacity 8):
  [1] alice
  [2] bob
  [3] carol
  [4] dave
  [5] erin
```

Notice how `capacity` jumps from 4 to 8 the moment the 5th record arrives.

## Check your work

Run under Valgrind to confirm every byte you `malloc`/`realloc` is freed and
that you never read or write out of bounds:

```sh
valgrind --leak-check=full ./db < input.txt
```

A correct solution reports **0 errors** and **all heap blocks freed**.

> **Bonus (optional):** print a message inside `db_add()` every time the array
> grows, e.g. `grew capacity to 8`. Feed the program many records and watch how
> rarely reallocations actually happen — that is the whole point of growing in
> chunks instead of one element at a time.
