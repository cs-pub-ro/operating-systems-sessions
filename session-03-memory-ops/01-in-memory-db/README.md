# Exercise: a growable in-memory database

`main.c` reads records from standard input into a heap array and prints them back at the end.
You never know in advance how many records there will be, so the array has to grow on demand.
You write that part.

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

The array is grown in **constant chunks**, never one record at a time, and it is **only ever expanded, never shrunk**:

```text
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

## Your tasks

Open `main.c` and complete the three TODOs:

1. **`db_init()`** — start empty: `records = NULL`, `count = 0`, `capacity = 0`.
1. **`db_add()`** — if `count == capacity`, grow the array by `CHUNK` records with `realloc` and check the result for `NULL`.
   Then copy the record into the slot at index `count` and increment `count`.
1. **`db_free()`** — free the array and reset the fields.

`realloc(NULL, size)` does the same thing as `malloc(size)`, so the same "grow when full" code also covers the very first allocation.

## Build

```console
make
```

## Run

Type records and finish with Ctrl-D, or pipe them in:

```console
printf '1 alice\n2 bob\n3 carol\n4 dave\n5 erin\n' | ./db
```

```text
Database holds 5 record(s) (capacity 8):
  [1] alice
  [2] bob
  [3] carol
  [4] dave
  [5] erin
```

Note how the capacity jumps from 4 to 8 the moment the fifth record arrives.

## Check your work

```console
valgrind --leak-check=full ./db < input.txt
```

A correct solution reports 0 errors and all heap blocks freed.
