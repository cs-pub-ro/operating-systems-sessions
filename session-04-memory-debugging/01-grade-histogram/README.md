# Exercise: the histogram that counts too much

`main.c` reads grades from standard input, rejects anything outside `0..100`, and counts each one into a ten-point bucket.
It compiles without a warning and never crashes, and the histogram it prints looks plausible.
It is still wrong.

## Reproduce

```console
make
./histogram < input.txt
```

`input.txt` holds 12 grades.
The program says it processed 13, and the bucket counts add up to 11.

Valgrind reports nothing, and that is expected: the bad write lands inside a block the allocator really did hand out, so it hits the wrong *field* rather than the wrong *block*.
For this one you need gdb.

## Your tasks

1. Find the out-of-bounds access with gdb.
   A conditional breakpoint and a watchpoint are the quickest way in:

    ```console
    gdb ./histogram
    (gdb) break record_grade if grade > 90
    (gdb) watch st->total
    ```

1. Fix it so that every valid grade, a perfect score of 100 included, is counted in the right bucket.
1. Check that the numbers agree — 12 grades in, 12 counted, bars adding up to 12:

    ```console
    ./histogram < input.txt
    printf '0\n100\n100\n' | ./histogram
    printf '101\n-5\n' | ./histogram
    ```

    The last one must reject both values and count nothing.

`main()` validates the input, which is what makes the code look airtight.
Validating the input is not the same as validating the index you compute from it.
