# heap-mayhem

A small "account vault" service: create accounts, list them, rename them, and audit them.
Every account gets audited on request -- nothing to worry about, right?

This challenge is built as a PIE (position-independent executable), unlike the other heap challenges in this session: every address is randomised on each run, and there is no obvious return-address or single-shot overflow to reach for.
You will need to combine an information leak with a heap overflow to get anywhere.

## Files

* `chall.c` -- the challenge source code.
* `chall` -- the compiled challenge binary.
  Run it locally with `./chall` (it looks for `flag.txt` in the current directory).

## Hints

1. The "list accounts" option prints a pointer that belongs to a function in this very binary.
   What does that tell you, once you also know that function's offset from the start of the binary?
1. `rename_account()` and `create_account()` are not the same operation -- one of them re-initialises fields that the other does not touch at all.
   Which one would you rather use to build your overflow?
1. Accounts are allocated back-to-back on the heap, in the order you create them.
   How far apart are two consecutively created accounts?
1. `objdump -d` will show you every function defined in this binary, including ones nothing in the visible menu ever calls.
