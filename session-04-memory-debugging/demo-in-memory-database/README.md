# Demo: debugging an in-memory database with gdb and Valgrind

This is the same growable in-memory database you wrote in the previous session — except this copy has **three memory bugs** in it.
None of them is a typo you can spot by staring at the file: every line looks reasonable on its own.

Your job here is not to guess.
It is to learn a **procedure**: run the program, observe how it fails, and then use a tool to walk backwards from the failure to the line that caused it.

We will fix the bugs one at a time, in the order the program shows them to us:

| # | Symptom | Tool that finds it |
|---|---------|--------------------|
| 1 | the program crashes with a segmentation fault | gdb |
| 2 | the program runs, but prints nonsense on the last line | gdb |
| 3 | the program prints everything correctly | Valgrind |

Notice the last row.
A program that produces the right output is **not** necessarily a correct program.

## What the program is supposed to do

It reads `<id> <name>` pairs from standard input into a heap array that grows by `CHUNK` records whenever it fills up, then prints:

1. every record in insertion order,
1. every record sorted by id,
1. which record was added first.

With `input.txt` the correct output is:

```text
Database holds 10 record(s) (capacity 12):
  [7] grace
  [3] carol
  ...
  [6] frank
Sorted by id:
  [1] alice
  [2] bob
  ...
  [10] judy
First record added: [7] grace
```

## Step 0: build with debug information

```console
make
```

The `Makefile` compiles with `-g -O0`, and that matters:

* **`-g`** puts the debug information (line numbers, variable names, types) into the binary.
  Without it gdb can only show you machine addresses, and Valgrind can only say "somewhere in this program" instead of naming a file and a line.
* **`-O0`** turns optimisations off.
  With `-O2` the compiler reorders and merges code, variables get "optimized out", and single-stepping jumps around in ways that are confusing while you are learning.
  Debug first, optimise later.

Debug information does not slow the program down and does not change what it does — it only makes the binary bigger.

---

# Bug 1: the crash

Run it:

```console
./db < input.txt
```

```text
Segmentation fault (core dumped)
```

Not a single line of output.
So the program dies **before** any printing, which means it dies while reading input — but where exactly, and why?

## Bringing up gdb

```console
gdb ./db
```

You get a `(gdb)` prompt.
The program is loaded but not running yet.
Start it, feeding it the input file exactly like on the shell:

```text
(gdb) run < input.txt
```

> `run` accepts the same redirections and arguments you would type in the shell.
> You can also set them once with `set args < input.txt` and then just type `run` (or `r`) after every rebuild.

gdb stops the program the moment it receives the fatal signal, instead of letting it die:

```text
Program received signal SIGSEGV, Segmentation fault.
0x0000555555555372 in db_add (db=0x7fffffffd8b0, id=7, name=0x7fffffffd8d0 "grace")
    at main.c:88
88		db->records[db->count].id = id;
```

This is already a lot: the crash is at **`main.c:88`**, inside `db_add`, while adding the record `7 grace` — the *first* record in the input file.
So the very first insertion kills the program.

## Where am I? `backtrace`

The most important gdb command is `backtrace` (`bt`): it prints the chain of function calls that led here.

```text
(gdb) bt
#0  0x0000555555555372 in db_add (db=0x7fffffffd8b0, id=7, name=0x7fffffffd8d0 "grace") at main.c:88
#1  0x00005555555556a3 in main () at main.c:161
```

Frame `#0` is where we crashed, frame `#1` is who called it.
`frame 1` (or `f 1`) would move you up to `main` so you can inspect *its* local variables; `frame 0` comes back down.
Use `list` (`l`) to print the source around the current line.

## Why? `print`

We are stopped at

```c
db->records[db->count].id = id;
```

A segfault on a line like this almost always means the pointer being dereferenced is not valid.
Ask gdb what it actually holds:

```text
(gdb) print *db
$1 = {records = 0x0, count = 0, capacity = 0}
```

There it is: `records` is `NULL`, `count` and `capacity` are `0`.
The array was never allocated.
But the code right above is supposed to allocate it when the database is full — and an empty database is certainly full.
Look at line 83:

```c
if (db->count == db->capacity - 1) {
```

Evaluate that condition yourself, in the live process:

```text
(gdb) print db->capacity - 1
$2 = 18446744073709551615
(gdb) print db->count == db->capacity - 1
$3 = 0
```

`0 - 1` is not `-1` here.
`capacity` is a **`size_t`**, an *unsigned* type, so subtracting one from zero wraps around to `SIZE_MAX` (2^64 - 1).
The condition is false, `db_grow()` is never called, and the store on line 88 writes through a `NULL` pointer.

> `print` is a full expression evaluator: it can dereference pointers (`print *db`), index arrays (`print db->records[0]`), call functions, and compare values.
> It is how you check an assumption instead of believing it.

## The fix

The array is full when `count == capacity`.
That is the whole rule; the `- 1` was never needed:

```c
if (db->count == db->capacity) {
```

Rebuild and rerun:

```console
make && ./db < input.txt
```

**Lesson:** mixing unsigned arithmetic with "one less than" is a classic C trap.
Any time you write `something - 1` on a `size_t`, ask what happens when `something` is `0`.
Note also that `-Wall -Wextra` did not say a word: the code is perfectly legal C, it just does not mean what the author thought.

---

# Bug 2: the wrong answer

Now the program runs to the end.
The two listings are correct, but the last line is not:

```text
Sorted by id:
  [1] alice
  ...
  [10] judy
First record added: [-1769714729]
```

The first record is `7 grace`, not `-1769714729` with an empty name.
Run it a second time:

```text
First record added: [-293104971]
```

**A different wrong answer on every run.** That is a fingerprint worth memorising: it means you are reading memory that nobody is maintaining any more — freed memory, or memory that was never initialised.
Correct code is deterministic; the addresses handed out by the allocator are not.

## Inspecting the moment of failure

The bad value is printed at `main.c:176`.
Stop there and look around:

```text
(gdb) break main.c:176
Breakpoint 1 at 0x1780: file main.c, line 176.
(gdb) run < input.txt
```

> `break` takes a `file:line` (`break main.c:176`) or a function name (`break db_add`).
> `info breakpoints` lists them, `delete 1` removes one.

```text
Breakpoint 1, main () at main.c:176
176			printf("First record added: [%d] %s\n", first->id, first->name);
(gdb) print first
$1 = (struct record *) 0x55555555a2b0
(gdb) print db.records
$2 = (struct record *) 0x55555555a480
(gdb) print *first
$3 = {id = 1431655770, name = "\005\000\000\000y\rN)\240o\331/", '\000' <repeats 19 times>}
(gdb) print db.records[0]
$4 = {id = 7, name = "grace", '\000' <repeats 26 times>}
```

The record itself is fine — `db.records[0]` is exactly `7 grace`.
The problem is that `first` points somewhere **else**: `0x...a2b0` instead of `0x...a480`.
Yet `main.c:169` assigned it from `&db.records[0]`.

So the array moved after `first` was taken.

## Catching the move: watchpoints

Instead of stepping through the whole input loop, ask gdb to stop whenever the *value of a variable changes*.
That is a **watchpoint**:

```text
(gdb) break main
(gdb) run < input.txt
(gdb) watch db.records
Hardware watchpoint 2: db.records
(gdb) continue
```

(We break in `main` first because `db` has to exist before we can watch it.)

```text
Hardware watchpoint 2: db.records
Old value = (struct record *) 0x0
New value = (struct record *) 0x55555555a2b0
db_grow (db=0x7fffffffd830) at main.c:72

(gdb) continue

Hardware watchpoint 2: db.records
Old value = (struct record *) 0x55555555a2b0
New value = (struct record *) 0x55555555a350
db_grow (db=0x7fffffffd830) at main.c:72

(gdb) continue

Hardware watchpoint 2: db.records
Old value = (struct record *) 0x55555555a350
New value = (struct record *) 0x55555555a480
db_grow (db=0x7fffffffd830) at main.c:72
```

The array is relocated **three times** while the input is being read, once per growth.
`db_grow()` allocates a bigger block, copies the records over and frees the old one (`main.c:62-68`).
The database's own pointer is updated, but `first` — a *copy* of the old address, made back at line 169 — is not.
From the first growth onwards, `first` points into a block that has already been freed.
The allocator has since reused those bytes for its own bookkeeping, which is why the printed id changes from run to run.

This bug is invisible in the source because both lines are individually correct.
What is wrong is the *lifetime* assumption connecting them.

## Valgrind's view of the same bug

Since we already know something is odd, this is a good moment to cross-check with the other tool:

```console
valgrind --leak-check=full ./db < input.txt
```

```text
==2750331== Invalid read of size 4
==2750331==    at 0x10978C: main (main.c:176)
==2750331==  Address 0x4a8a080 is 0 bytes inside a block of size 144 free'd
==2750331==    at 0x484988F: free (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==2750331==    by 0x109330: db_grow (main.c:68)
==2750331==    by 0x109386: db_add (main.c:84)
==2750331==    by 0x1096E9: main (main.c:161)
==2750331==  Block was alloc'd at
==2750331==    at 0x4846828: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==2750331==    by 0x1092D4: db_grow (main.c:62)
==2750331==    by 0x109386: db_add (main.c:84)
==2750331==    by 0x1096E9: main (main.c:161)
```

Read it as a story: *"line 176 read 4 bytes from a block that was allocated at line 62 and freed at line 68."* Valgrind tells you the whole life of the block — where it was born, where it died, and where you touched its corpse. gdb showed you *the mechanism*; Valgrind hands you *the timeline*.
Use both.

## The fix

Never hold a pointer into a buffer that can be reallocated.
Either copy the data out, or remember the **index** and re-derive the pointer when you need it (`db.records[0]`, always read through the current `db.records`).
See `solution.c`:

```c
if (db.count == 1) {
	first_id = db.records[0].id;
	strncpy(first_name, db.records[0].name, NAME_LEN - 1);
	first_name[NAME_LEN - 1] = '\0';
	have_first = 1;
}
```

**Lesson:** the moment a container may grow, every pointer into it becomes suspect.
This is the same rule as iterator invalidation in C++ or slice aliasing in Go, and it is the single most common bug in hand-written dynamic arrays.

---

# Bug 3: the silent one

Rebuild and run again.
The output is now exactly right — all ten records, the sorted listing, `First record added: [7] grace`.
As far as the terminal is concerned, the program is finished.

It is not.
Ask Valgrind:

```console
valgrind --leak-check=full ./db < input.txt
```

```text
==2750331== HEAP SUMMARY:
==2750331==     in use at exit: 360 bytes in 1 blocks
==2750331==   total heap usage: 6 allocs, 5 frees, 9,416 bytes allocated
==2750331==
==2750331== 360 bytes in 1 blocks are definitely lost in loss record 1 of 1
==2750331==    at 0x4846828: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==2750331==    by 0x109551: db_print_sorted (main.c:128)
==2750331==    by 0x109778: main (main.c:173)
==2750331==
==2750331== LEAK SUMMARY:
==2750331==    definitely lost: 360 bytes in 1 blocks
```

Three numbers tell the whole story:

* **`6 allocs, 5 frees`** — one block was never released.
* **`360 bytes`** — 10 records × 36 bytes: the scratch array of `db_print_sorted()`.
* **`definitely lost`** — at exit, no pointer to that block existed anywhere in the program, so it could not possibly have been freed later.
  (Compare with *still reachable*: memory you were holding a pointer to at exit — usually a cache or a global; and *possibly lost*, where only an interior pointer remained.)

The stack trace under "definitely lost" is the **allocation** site, not the place where the leak "happened" — a leak has no single moment, it is the *absence* of an event.
`db_print_sorted()` allocates a private copy at line 128, sorts it, prints it and returns without ever calling `free`.

This is exactly the class of bug gdb cannot help you with.
There is nothing to break on, no wrong value to print, no crash.
The program is well-behaved right up to the point where a long-running version of it exhausts the machine's memory.

## The fix

Whoever allocates a scratch buffer frees it before returning:

```c
	for (size_t i = 0; i < db->count; i++)
		printf("  [%d] %s\n", sorted[i].id, sorted[i].name);

	free(sorted);
}
```

**Lesson:** for every allocation, decide *who owns the block* and *where it dies*, at the moment you write the `malloc`.
A block that is local to one function should be freed on **every** exit path of that function — including the early `return`s in the error branches.

---

# Confirming the repair

```console
make sol
valgrind --leak-check=full ./db-sol < input.txt
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

**"All heap blocks were freed"** plus **"0 errors from 0 contexts"** is the result you should be aiming for in every assignment from now on.
`solution.c` contains the three fixes, each marked with a `FIX n` comment.

---

# gdb quick reference

Everything used above, plus the handful of commands you will need next.
Most have one-letter or short abbreviations (`r`, `b`, `c`, `n`, `s`, `p`, `bt`).

**Starting and running**

| Command | What it does |
|---------|--------------|
| `gdb ./db` | load the program (built with `-g`) |
| `run` / `r` | start it; `run < input.txt` redirects stdin, `run arg1 arg2` passes arguments |
| `start` | run and stop at the first line of `main` |
| `continue` / `c` | resume until the next breakpoint or crash |
| `kill` | stop the running program |
| `quit` / `q` | leave gdb |

**Stopping at the right place**

| Command | What it does |
|---------|--------------|
| `break main.c:88` | stop at a line |
| `break db_add` | stop on entry to a function |
| `break db_add if id == 100` | stop only when the condition holds — invaluable inside loops |
| `watch db.records` | stop when the *value* of an expression changes |
| `info breakpoints` | list breakpoints and watchpoints |
| `delete 2` / `disable 2` | remove / temporarily switch off number 2 |

**Moving one step at a time**

| Command | What it does |
|---------|--------------|
| `next` / `n` | execute the current line, stepping **over** calls |
| `step` / `s` | execute the current line, stepping **into** calls |
| `finish` | run until the current function returns (and print its return value) |
| `until N` | continue until line N — handy for escaping a loop |

**Looking around**

| Command | What it does |
|---------|--------------|
| `backtrace` / `bt` | the call stack that got you here |
| `frame 1` / `f 1` | switch to another stack frame |
| `up` / `down` | move one frame towards `main` / back |
| `list` / `l` | show the source around the current line |
| `print expr` / `p` | evaluate anything: `p *db`, `p db->records[2]`, `p i * 4`, `p/x count` (hex) |
| `info locals` | all local variables of the current frame |
| `info args` | the arguments of the current function |
| `x/4dw ptr` | examine raw memory: 4 decimal words at `ptr` (`x/16xb` = 16 hex bytes) |
| `ptype struct database` | show a type definition |
| `tui enable` | split the terminal and follow the source as you step (`Ctrl-x a` toggles) |

**Handy detail:** gdb disables address-space randomisation by default, so addresses are reproducible between runs *inside* gdb even though they change outside it.

# gdb or Valgrind?

They answer different questions, and neither replaces the other:

* **gdb** is a *microscope on one run*.
  It answers "what is the value of this variable right now?", "how did control get here?", "who changed this?".
  It needs a symptom to aim at: a crash, or a value you can tell is wrong.

* **Valgrind (memcheck)** is an *auditor of the whole run*.
  It re-runs your program with every memory access checked and reports invalid reads and writes, use of uninitialised values, double frees and leaks — including the ones that did not visibly break anything on this particular input.

The practical workflow: **run Valgrind first** to find out *what* is wrong and *where*, then reach for **gdb** to understand *why* — and always run Valgrind once more at the end to confirm there is nothing left it can see.
