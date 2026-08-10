# heap-mayhem

**heap-mayhem** is a bonus heap-exploitation challenge, one notch harder than `heap-havoc`: the binary is built as a PIE, so there is no fixed address to hardcode -- the exploit has to leak one first.

## Requirements

The only requirement to build, publish, deploy, and solve this challenge is **Docker**.

## The bug

Each "account" is a heap struct:

```c
struct account {
        char name[24];
        long balance;
        void (*audit)(const struct account *);
};
```

`rename_account()` overwrites an **already-allocated** account's `name` with `scanf("%s", ...)` -- no length check, and critically, unlike `create_account()`, it never re-initialises `balance`/`audit` afterwards.
Accounts are allocated back-to-back on the heap in creation order, so a long enough new name overflows past this account's own fields and into the *next* account's `balance` and `audit` fields.

Nothing in the visible menu ever sets `audit` to anything except `default_audit` -- except there is a second function, `secret_audit()`, that prints the flag and that nothing ever calls.

## Defeating ASLR: the leak

`list_accounts()` prints, among other things, each account's `audit` function pointer.
For an account nobody has tampered with, that pointer is the runtime address of `default_audit()` -- a legitimate code address inside this very binary.
Since the offset of `default_audit` (and `secret_audit`) from the start of the binary is fixed and known (from the ELF symbol table), one leaked pointer is enough to compute the binary's load base, and from there, `secret_audit()`'s absolute runtime address:

```python
base = leaked_default_audit_addr - default_audit_offset
secret_addr = base + secret_audit_offset
```

## The exploit

1. Create account 0 (`leak-me`) and account 1 (`victim`) -- account 1 is allocated immediately after account 0.
1. `list_accounts()` leaks account 0's `audit` pointer and both accounts' heap addresses (the *distance* between two consecutively created accounts is measured at runtime here too, rather than hardcoded).
1. Compute `secret_audit()`'s address as above.
1. **Rename account 0** with a payload long enough to reach past its own `name`+`balance`+`audit`, past the gap to account 1's start, past account 1's own `name`+`balance`, and land exactly on account 1's `audit` field -- overwriting it with `secret_audit()`'s address.
1. **Run audit on account 1.** It calls `secret_audit()` instead of `default_audit()`, which prints the flag.

See `solve/exploit.py` for the full script; it recomputes every offset from the leak at runtime, so it works unmodified against any run of the binary (any ASLR base).

## Challenge structure

* **`build/`** -- source and a reproducible Docker build environment (default PIE).
* **`publish/`** -- packages the binary and matching libc/loader.
* **`deploy/`** -- runs the binary under `xinetd` in a container, exposed on port `31021`.
  ASLR is **not** disabled -- the exploit has to work against a genuinely randomised target, same as `heap-mayhem`'s design intent.
* **`solve/`** -- `exploit.py`.
  Needs the binary mounted (even for remote solving) to read `default_audit`/`secret_audit`'s offsets from the ELF symbol table.

## The flag

Stored in the `flag` file in this directory; copied into the deployed container as `flag.txt` next to the binary.

## Getting started

Start with `build/README.md`, then `publish/README.md`, `deploy/README.md`, and `solve/README.md` in order.
