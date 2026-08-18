# Exercise: implement `strlen`, `strcpy`, `strcat`, `memcpy`

Write four of the C library's string functions yourself, test them, then measure them.

## Your tasks

Open `mystring.c` and fill in the four TODOs.
That is the only file you change.

| function | what it must do |
| --- | --- |
| `my_strlen` | length up to, not including, the `'\0'` |
| `my_strcpy` | copy a string, `'\0'` included; return `dest` |
| `my_strcat` | append to the string in `dest`; return `dest` |
| `my_memcpy` | copy exactly `n` bytes; knows nothing about `'\0'`; return `dest` |

**Do not call anything from `<string.h>`** — that is the whole point.

Two things to watch: `my_strcpy` must copy the `'\0'` as well, and `my_memcpy` takes `void *`, which you cannot dereference before assigning it to an `unsigned char *`.

## Build and test

Write a few tests of your own first, then run the provided suite:

```console
make test
```

You should end at `25/25 checks passed`.

## Measure

Both columns append the same 16-byte chunk N times, one with `my_strcat` and one with `my_memcpy`:

```console
make bench
```

Every time N doubles, `my_strcat` takes 4× longer, while `my_memcpy` merely doubles.
`memcpy` is told how many bytes to copy; `strcat` is not told where `dest` ends, so it walks the whole string again on every call.

## Check yourself

* You append 1 000 chunks and it takes 2 ms.
  Roughly how long for 4 000?
* Why can `memcpy` copy through an embedded `'\0'` when `strcpy` cannot?
* glibc's `strcat` is written in hand-tuned assembly and is still slower here than your byte-at-a-time `my_memcpy`.
  Explain that in one sentence.
