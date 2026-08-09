# demo-heap-1

**demo-heap-1** is a warm-up heap-exploitation challenge, meant to be
solved together by the teaching assistant and students at the start of
the session. It is deliberately very close to `02-cylab-heap-1` (same
bug, same overflow distance, different variable names/theme), so that
having solved it once, `02-cylab-heap-1` should go quickly.

## Requirements

The only requirement to build, publish, deploy, and solve this challenge
is **Docker**.

## The bug

Same layout as `demo-heap-0`: `diary_entry` and `access_level` are two
adjacent 5-byte heap allocations, and `write_diary()`'s
`scanf("%s", ...)` has no length limit, so overflowing `diary_entry`
reaches into `access_level`.

Unlike `demo-heap-0`, the win condition requires an exact match:

```c
if (!strcmp(access_level, "root")) {
        /* print the flag */
}
```

`access_level` starts out equal to `"user"`; it has to become exactly
`"root"`.

## The exploit

Same overflow distance as `demo-heap-0` (32 bytes), with the exact target
string as the payload's tail:

```python
payload = b"A" * 32 + b"root"
```

See `solve/exploit.py`.

## Challenge structure

Same 4-stage layout as every other challenge in this session:
`build/` -> `publish/` -> `deploy/` (port `31001`) -> `solve/`.

## The flag

Stored in the `flag` file in this directory; copied into the deployed
container as `flag.txt` next to the binary.
