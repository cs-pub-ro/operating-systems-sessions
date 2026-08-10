# demo-heap-0

**demo-heap-0** is a warm-up heap-exploitation challenge, meant to be solved together by the teaching assistant and students at the start of the session.
It is deliberately very close to `01-cylab-heap-0` (same bug, same overflow distance, different variable names/theme), so that having solved it once, `01-cylab-heap-0` should go quickly.

## Requirements

The only requirement to build, publish, deploy, and solve this challenge is **Docker**.

## The bug

`init()` allocates two adjacent 5-byte buffers on the heap:

```c
diary_entry = malloc(DIARY_ENTRY_SIZE);   /* "meh." */
lock_state  = malloc(LOCK_STATE_SIZE);    /* "shut" */
```

`write_diary()` copies player input into `diary_entry` with `scanf("%s", diary_entry)` -- no length limit.
Writing more than the usable chunk size overflows into `lock_state`, which sits right after it on the heap.

The win condition is inverted: `lock_state` starts out equal to `"shut"`, and `check_win()` prints the flag as soon as it is anything else.

## The exploit

Same shape as `01-cylab-heap-0`: 32 filler bytes reach `lock_state`, then anything non-empty overwrites `"shut"`:

```python
payload = b"A" * 32 + b"XXXX"
```

See `solve/exploit.py`.

## Challenge structure

Same 4-stage layout as every other challenge in this session: `build/` -> `publish/` -> `deploy/` (port `31000`) -> `solve/`.

## The flag

Stored in the `flag` file in this directory; copied into the deployed container as `flag.txt` next to the binary.
