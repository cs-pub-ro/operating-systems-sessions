# Solution: mini JSON parser/serializer

This is the reference (bug-free) implementation of the JSON parser exercise.
If you were sent here from `bonus-json-parser/`, this directory shows what a
correct fix looks like — try to find and fix the bug yourself first.

## What it is

A small in-memory JSON library:

- `json_value.h` — the public interface: the tagged-union `json_value_t`
  type, the ownership rule ("a container owns every child stored in it"),
  and the parser/serializer/constructor prototypes.
- `json_value.c` — the implementation: a recursive-descent parser, a
  single-line serializer, and a growable string buffer (`strbuf_t`) used
  while decoding string literals (including `\"`, `\\`, `\uXXXX`, etc).
- `main.c` — parses a well-formed document, prints and round-trips it
  through the serializer, feeds the parser two different kinds of malformed
  input to confirm it rejects them without crashing or leaking, and builds a
  small tree by hand with the constructor API (`json_new_object()`,
  `json_object_set()`, `json_array_append()`, ...).

## Build, run, test

```sh
make
./jsontool
```

Confirm there is nothing left for Valgrind to complain about:

```sh
valgrind --leak-check=full ./jsontool
```

```
==...== HEAP SUMMARY:
==...==     in use at exit: 0 bytes in 0 blocks
==...==   total heap usage: 98 allocs, 98 frees, ... bytes allocated
==...==
==...== All heap blocks were freed -- no leaks are possible
==...==
==...== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

## Design note worth carrying into the buggy version

- **String buffers always allocate `len + 1` bytes.** `strbuf_finish()`
  hands the caller a string with room for the trailing `'\0'` in addition to
  every character that was pushed with `strbuf_putc()`. Allocating exactly
  `len` bytes and then writing the terminator at `result[len]` would write
  one byte past the end of the block — invisible on most runs (the output
  can still look completely correct), but a guaranteed heap corruption that
  Valgrind reliably reports as an invalid write.
