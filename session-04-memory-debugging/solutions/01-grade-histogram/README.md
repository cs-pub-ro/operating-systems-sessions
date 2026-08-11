# Solution: the histogram that counts too much

This is the reference (bug-free) implementation of the grade histogram exercise in [`01-grade-histogram`](../../01-grade-histogram).

## The bug

`record_grade()` derived the bucket index straight from the grade:

```c
int bucket = grade / 10;
```

For a grade of 100 that yields `10`, one past the end of `counts[NBUCKETS]`.
Nothing crashed, because the memory just after `counts[]` is still inside `struct stats` — it is the `total` field.
So a perfect score was not counted in any bucket *and* silently incremented the record count a second time, which is why 12 grades in produced bars adding up to 11 and a reported total of 13.

The fix clamps the last bucket so that `90..100` all land in `counts[NBUCKETS - 1]`; see the `FIX` comment in `main.c`.

The lesson: validating the **input** (`0..100`) is not the same as validating the **index** you derive from it.
Valgrind cannot catch this one — memcheck knows where each allocated block begins and ends, but a write that lands on the wrong field *inside* a block it legitimately gave you looks exactly like a correct one. That is what gdb watchpoints are for.

Files:

* `main.c` — the fixed implementation.
* `input.txt` — the 12 sample grades.

## Build and run

```console
make
./histogram < input.txt
```

```text
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
The edge cases behave too:

```console
printf '0\n100\n100\n' | ./histogram
printf '101\n-5\n' | ./histogram      # both rejected, nothing counted
```
