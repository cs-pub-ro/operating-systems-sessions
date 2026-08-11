# Bonus exercise: make your library — static vs dynamic linking

In the string-functions exercise you wrote `my_strlen`, `my_strcpy`, `my_strcat` and `my_memcpy`.
That is already a library's worth of code — it just happened to get compiled into the same program that used it.

Now we do the real thing: turn it into `libmystring`, ship it in both flavours, link a separate program against each, and measure the difference.

At the end you will have built, by hand, the two things `-lc` has been silently giving you since your first `printf`.

## Setup

Copy your solution from the string-functions exercise into this directory:

```console
cp ../01-string-functions/mystring.c ../01-string-functions/mystring.h .
make
```

`main.c` is already here and does not need changing.
It calls your three functions in a tight loop and times them.

## Part A — the static library (`.a`)

Two steps:

```console
gcc -O2 -c mystring.c -o mystring.o    # 1. compile to an object file
ar rcs libmystring.a mystring.o        # 2. bundle object files into an archive
```

`ar` is an *archiver*, not a linker.
A `.a` file is little more than a **bag of `.o` files with an index** — closer to a `.tar` than to a program.
You can prove it:

```console
ar t libmystring.a      # list members
ar x libmystring.a      # extract them back out
```

Link against it:

```console
gcc -O2 -o main_static main.c -L. -Wl,-Bstatic -lmystring -Wl,-Bdynamic
```

* `-L.` — look for libraries in this directory.
* `-lmystring` — link a library named `mystring`, i.e. look for `libmystring.so` first, then `libmystring.a`.
  (The `lib` prefix and the extension are added *by the linker*.
  This is why the file must be named `libmystring.a` and not `mystring.a`.)
* `-Wl,-Bstatic` — for libraries named after this, prefer the `.a`.
  **Needed here**, because both `libmystring.a` and `libmystring.so` exist and the linker would otherwise pick the `.so`.
* `-Wl,-Bdynamic` — switch back, so that **libc** is still linked dynamically.
  Forget this and the linker will try to link libc statically as well.

At link time the linker copies the machine code of the functions you actually used **into your executable**.
After that, `libmystring.a` is irrelevant — you can delete it and `main_static` still runs.

## Part B — the shared library (`.so`)

```console
gcc -O2 -fPIC -c mystring.c -o mystring_pic.o   # 1. position-independent code
gcc -shared -o libmystring.so mystring_pic.o    # 2. link into a shared object
gcc -O2 -o main_dynamic main.c -L. -lmystring   # 3. link the program
```

### Why `-fPIC`?

**P**osition-**I**ndependent **C**ode.
A `.so` can be mapped at a different address in every process that loads it — the loader decides at run time, and the same library is shared by many processes at once.
So the code cannot contain hardcoded absolute addresses; it refers to its own data via a table (the GOT, see below) instead.

This is the price of sharing, and it is exactly what makes dynamic calls slightly slower.

### Now run it

```console
./main_dynamic 1000
```

```text
./main_dynamic: error while loading shared libraries: libmystring.so:
cannot open shared object file: No such file or directory
```

**This is supposed to happen.**
It is the single most common linking error you will hit, so understand it now.

`-L.` told the **linker**, at build time, where to find the library.
It said nothing to the **loader**, at run time.
The loader (`ld.so`) does not know or care about `-L`; it searches `/lib`, `/usr/lib`, and a few configured places.
`.` is not among them — and for good reason: running whatever `libmystring.so` happens to sit in the current directory would be a fine way to get your program hijacked.

Three ways to fix it:

```console
# 1. Tell the loader where to look, for this run only.
LD_LIBRARY_PATH=. ./main_dynamic 1000        # this is what `make run-dynamic` does

# 2. Bake the search path into the executable at link time ($ORIGIN = "the
#    directory the executable is in"). This is what real projects usually do.
gcc -O2 -o main_rpath main.c -L. -lmystring -Wl,-rpath,'$ORIGIN'
./main_rpath 1000                             # just works

# 3. Install it system-wide (needs root).
sudo cp libmystring.so /usr/local/lib/ && sudo ldconfig
```

Confirm which library got picked with `ldd`:

```console
LD_LIBRARY_PATH=. ldd main_dynamic
```

## Part C — look at what you built

```console
make inspect
```

### The `.so` is not in the executable

```text
$ nm -u main_static  | grep my_strlen
(nothing — the code is inside the binary)

$ nm -u main_dynamic | grep my_strlen
                 U my_strlen                 <- U = Undefined: "find this at run time"
```

```text
$ ldd main_dynamic
	libmystring.so => ./libmystring.so (0x00007f3528a1e000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f3528600000)
	/lib64/ld-linux-x86-64.so.2                      <- the loader itself
```

`main_static` lists only libc; its copy of `my_strlen` came along for the ride.

### The call site is literally different

This is the whole difference, in one line each:

```text
main_static  :  call 1440 <my_strlen>        <- direct call, straight there
main_dynamic :  call 10d0 <my_strlen@plt>    <- call a stub in the PLT
```

`main_dynamic` cannot contain the address of `my_strlen`: nobody knows it until `libmystring.so` is mapped.
So the compiler emits a call to a local **stub**, and the stub jumps to whatever address the loader eventually writes down:

```text
your code  --call-->  PLT stub  --jmp *GOT(%rip)-->  the real my_strlen
                      (Procedure      (Global Offset Table:
                       Linkage         a table of addresses
                       Table)          filled in by the loader)
```

By default the resolution is **lazy**: the GOT initially points back into the loader, so the *first* call to each function goes the long way round and gets patched; later calls are just one extra indirect jump.
(`LD_BIND_NOW=1` forces all of it to happen at start-up instead.)

That extra indirect jump — every call, forever — is what we are about to measure.

## Part D — measure

```console
make bench      # steady-state call cost
make startup    # process start-up cost
```

`make bench` interleaves the binaries and repeats 5 times **on purpose**: the effect we are chasing is smaller than the run-to-run noise, so one run of each proves nothing.

### Call cost

Ubuntu 24.04, gcc 13.3, 20 000 000 iterations × 3 calls.
Five rounds:

| | ns/call (5 rounds) | mean |
| --- | --- | --- |
| `main_static` | 5.50, 5.49, 5.39, 5.53, 5.18 | **5.42** |
| `main_dynamic` | 6.35, 6.18, 6.07, 5.95, 6.42 | **6.19** |
| `main_fullstatic` | 5.99, 6.10, 5.80, 5.88, 5.74 | **5.90** |

Dynamic linking costs about **0.8 ns per call, roughly 14%**.

Notice *why* this is believable: the static range (5.18–5.53) and the dynamic range (5.95–6.42) **do not overlap**.
Static won all five rounds.
A single pair of runs 14% apart would have proved nothing — the same binary varies by ~7% between rounds.

0.8 ns is about 2–3 clock cycles: an extra indirect jump, plus a branch predictor that has to learn one more target.
That is the PLT, and it matches the disassembly exactly.

### Start-up cost

200 runs each of `./main 0` (0 iterations = start up and exit immediately):

| | 200 runs | per process |
| --- | --- | --- |
| `main_fullstatic` | 0.50 s | 2.51 ms |
| `main_static` | 0.53 s | 2.65 ms |
| `main_dynamic` | 0.60 s | 2.98 ms |

One extra `.so` costs about **330 µs of start-up** — mapping the file, relocating it, and resolving symbols, before `main` runs at all.

Put the two measurements together:

> 330 µs of extra start-up ÷ 0.8 ns per call ≈ **430 000 calls** before the per-call overhead even *matches* what you already paid to load the library.
>
> For most programs, dynamic linking's real cost is **start-up, not calls**.
> This is why start-up time is a big deal for things that run constantly and briefly — shell utilities, CGI scripts, `git` — and irrelevant for a long-running server.

## So why does anything use dynamic linking?

Static won *both* measurements.
Yet essentially everything on your system is dynamically linked.
Look at the size column from `make inspect`:

| | text (bytes) |
| --- | --- |
| `main_static` | 3 047 |
| `main_dynamic` | 3 040 |
| `main_fullstatic` | 668 981 |

`main_fullstatic` carries its own private copy of libc — **220× bigger**.
Now imagine that for all ~2 000 binaries in `/usr/bin`.

| | static | dynamic |
| --- | --- | --- |
| call cost | ~5.4 ns | ~6.2 ns (+14%) |
| start-up | faster | +~330 µs per `.so` |
| disk | one copy of libc **per program** | one copy **total** |
| RAM | one copy per process | **one copy shared by every process** |
| security fix in libc | rebuild + redistribute **every** program | replace one file |
| upgrade a library | relink everything | drop in a new `.so` |
| plugins (`dlopen`) | impossible | the entire point |
| missing `.so` at run time | cannot happen | your program will not start |

The shared-RAM row is the one that decides it.
`libc.so` is loaded into memory **once** and shared, read-only, by every process on the machine — that is what the "shared" in "shared library" means, and it is the feature the whole design exists for.
Statically linking everything would multiply that by the number of running processes.

> **The real lesson.**
> Dynamic linking is measurably slower on both metrics we tested, and it is still the right default — because RAM, disk, and the ability to ship a security patch without rebuilding the world matter more than 0.8 ns.
> "Which is faster?" was the wrong question.
> Engineering is choosing which cost you would rather pay.

This is the same shape of argument as the `printf` vs `write` demo: buffered `printf` beat raw `write` not because the library was clever, but because it made a different trade.
Measure, then decide what you are optimising *for*.

## Things to try

1. **Delete the library and re-run.**
   `rm libmystring.a && ./main_static` — still fine.
   `rm libmystring.so && LD_LIBRARY_PATH=. ./main_dynamic` — dead.
   Explain both in one sentence each.
1. **Change the library without recompiling the program.**
   Edit `mystring.c` to make `my_strlen` always return 42, rebuild *only* `libmystring.so` (`make libmystring.so`), and re-run the **unchanged** `main_dynamic`.
   Then try the same with `main_static`.
   This is what a security update looks like.
1. **`LD_BIND_NOW=1 ./main_dynamic 20000000`** — forces eager symbol resolution.
   Predict the effect on start-up and on call cost separately, then measure.
   Were you right?
1. **`main_fullstatic` is consistently ~9% slower than `main_static`** (5.90 vs 5.42 ns/call), even though both use direct calls and neither touches libc in the loop.
   Why?
   Hints: is `main_static` a PIE and `main_fullstatic` not? (`file main_static`) Does code alignment change? (`objdump -d`)
   This one is genuinely open — a good excuse to use `perf` if you can lower `perf_event_paranoid`.
1. **`-fno-plt`**: try `gcc -O2 -fno-plt -o main_noplt main.c -L. -lmystring`.
   What does the call site look like now (`objdump -d`)?
   Does it help?
1. **`LD_DEBUG=all ./main_dynamic 0 2>&1 | head -50`** — watch the loader work.
   Try `LD_DEBUG=bindings` too.
   This is the 330 µs, itemised.
1. **Symbol interposition**: write a `my_strlen` in a second `.so` and `LD_PRELOAD` it in front of `main_dynamic`.
   Why can you do this to a dynamically linked program and not to a static one? (This is how `valgrind` and many profilers work — and also how malware hooks functions.)

## Check yourself

* Why does `-L.` not help at run time?
* Your program links `libfoo.so`.
  You rebuild `libfoo.so` with an extra function.
  Do you have to relink your program?
  What if you *remove* a function?
* Why must a `.so` be compiled `-fPIC` but a `.a` need not?
* A colleague proposes statically linking everything at your company "because it is 14% faster per call".
  Give the two strongest arguments against.
* Which of the three binaries would you ship as a command-line tool that users run thousands of times in a shell loop?
  Which as a long-running daemon?
