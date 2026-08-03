# Exercise 1: the histogram that counts too much

`main.c` builds a histogram of grades. It reads integers from standard input,
rejects anything outside the `0..100` range, and counts each grade into one of
ten ten-point buckets:

```c
#define NBUCKETS	10

struct stats {
	int counts[NBUCKETS];	/* how many grades landed in each bucket */
	int total;		/* how many grades we processed in total  */
};
```

The program compiles without a single warning, never crashes, and prints a
perfectly plausible histogram. It is still wrong.

## Reproduce the failure

```sh
make
./histogram < input.txt
```

```
  0 -   9 |  0
 10 -  19 |  0
 20 -  29 |  0
 30 -  39 | # 1
 40 -  49 | # 1
 50 -  59 | # 1
 60 -  69 | ## 2
 70 -  79 | ## 2
 80 -  89 | ## 2
 90 - 100 | ## 2
processed 13 grades
```

Two things do not add up — literally:

```sh
wc -l input.txt        # 12 grades in the file...
```

- the program claims it processed **13** grades;
- the ten bucket counts add up to **11**.

Twelve grades went in. Neither number that came out is twelve, and the two do
not even agree with each other. Somewhere a count is being incremented that
should not be, and somewhere a grade is not being counted at all.

## First, try Valgrind

```sh
valgrind ./histogram < input.txt
```

```
==2744749== All heap blocks were freed -- no leaks are possible
==2744749== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

**Valgrind sees nothing wrong.** That is not a bug in Valgrind, and it is worth
understanding before you go on: memcheck works at the granularity of *blocks
returned by the allocator*. It knows where each `malloc`/`calloc` block starts
and ends, so it catches writes that fall outside those bounds — but a write
that lands on the wrong field *inside* a block it legitimately gave you is
indistinguishable, to memcheck, from a correct one.

So for this bug you need the other tool.

## Find it with gdb

```sh
gdb ./histogram
(gdb) run < input.txt
```

Suggestions, roughly in increasing order of cleverness — you do not need all of
them:

- Break on the function that does the counting and step through it for one
  grade at a time (`break record_grade`, then `next`, `print`, `continue`).
  Twelve grades is a lot of stepping, though.
- Print the state as you go: `print *st`, `print st->counts`, `print st->total`.
  `print` understands whole arrays and structures, so you can watch the entire
  histogram evolve.
- **Use a conditional breakpoint** to stop only on the input you suspect:
  `break record_grade if grade > 90`. Which grade in `input.txt` is unlike all
  the others?
- Inside `record_grade`, check that the index really is in range before it is
  used. gdb will tell you how big the array is:
  `print sizeof(st->counts) / sizeof(st->counts[0])`.
- **Use a watchpoint** on the field that is too large: `watch st->total`, then
  `continue` repeatedly. gdb stops after *every* write to it and shows you the
  line responsible. One of those stops will be at a line that has no business
  touching `total` at all.

That last observation is the heart of the exercise: the two fields of
`struct stats` are neighbours in memory, so writing one element past the end of
`counts[]` writes straight into `total`. Nothing crashes, because that memory
is perfectly valid — it just belongs to something else.

## Your task

1. Find the out-of-bounds access with gdb.
2. Fix it so that **every** valid grade — including a perfect score of 100 — is
   counted in the right bucket.
3. Convince yourself the fix is right:

```sh
./histogram < input.txt
```

```
  0 -   9 |  0
 10 -  19 |  0
 20 -  29 |  0
 30 -  39 | # 1
 40 -  49 | # 1
 50 -  59 | # 1
 60 -  69 | ## 2
 70 -  79 | ## 2
 80 -  89 | ## 2
 90 - 100 | ### 3
processed 12 grades
```

Twelve grades in, twelve grades counted, bars adding up to twelve.

Test the edges as well — they are where this kind of bug lives:

```sh
printf '0\n100\n100\n' | ./histogram
printf '101\n-5\n' | ./histogram      # both must be rejected, nothing counted
```

## Takeaway

The input validation in `main()` rejects everything outside `0..100`, which
makes the code *look* airtight — and it is the reason the bug survived review.
Validating the **input** is not the same as validating the **index** you derive
from it. Whenever you compute an array index from data, ask what the largest
value the formula can produce is, and compare it with the size of the array.
