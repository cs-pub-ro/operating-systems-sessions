This program mishandles memory.
Can you exploit it to get the flag?

Link: https://learn.cylabacademy.org/library/440

## Files

- `chall.c` -- the challenge source code.
- `chall` -- the compiled challenge binary. Run it locally with `./chall`
  (it looks for `flag.txt` in the current directory).

## Hints

1. Check out "use after free".
1. `free()` does not clear the pointer that was passed to it -- the
   program can still read and write through it afterwards.
1. If you allocate a new object of the right size right after freeing
   the old one, what might the allocator hand you back?

