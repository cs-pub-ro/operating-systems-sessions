# Solution: symbol hash table

This is the reference (bug-free) implementation of the symbol hash table exercise.
If you were sent here from `03-symbol-hash-table/`, this directory shows what a correct fix looks like — try to find and fix the three bugs yourself first.

## What it is

A small hash table mapping a program's symbol names (as you would see them in `nm` or `objdump`) to two pieces of information:

* the address the symbol lives at, and
* which memory region of the process image owns that address: `.text` (code), `.data` (initialised globals), `.rodata` (string literals and other read-only constants) or `.bss` (zero-initialised globals).

Collisions are resolved with separate chaining: `symbol_hash_table_t::buckets` is an array of linked-list heads, and the djb2 string hash picks the bucket.

Files:

* `symbol_hash_table.h` — the public interface: types and function prototypes.
* `symbol_hash_table.c` — the implementation.
* `main.c` — a small driver that inserts a batch of symbols into a deliberately small (8-bucket) table, forcing hash collisions, then looks symbols up, updates one, removes one, and prints the table before and after.

## Build, run, test

```console
make
./symtab
```

Expected output: every inserted symbol printed once, grouped by bucket, with its address and region name; a successful lookup of `compute_sum`; a failed lookup of `does_not_exist`; the updated address of `g_version`; and the table with one fewer entry after `g_retry_limit` is removed.

Confirm there is nothing left for Valgrind to complain about:

```console
valgrind --leak-check=full ./symtab
```

```text
==...== HEAP SUMMARY:
==...==     in use at exit: 0 bytes in 0 blocks
==...==   total heap usage: 27 allocs, 27 frees, ... bytes allocated
==...==
==...== All heap blocks were freed -- no leaks are possible
==...==
==...== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

## Design notes worth carrying into the buggy version

* `symtab_create()` uses `calloc()` for the bucket array specifically so that every bucket head starts out `NULL` — a freshly allocated `malloc()`ed array would contain garbage pointers instead.
* Every node inserted with `symtab_insert()` explicitly sets `entry->next` before linking it into the bucket (`entry->next = table->buckets[index];`) — never assume a freshly `malloc()`ed struct field is zero.
* `symtab_remove()` always repairs whichever pointer refers to the node being removed: `table->buckets[index]` if it is the first node in the chain, or `prev->next` otherwise.
  Skipping this step leaves a dangling pointer to freed memory sitting in the table.
* Every `strdup()` has a matching `free()`: one in `symtab_remove()` for a single removed entry, and one per entry in the loop inside `symtab_destroy()`.
