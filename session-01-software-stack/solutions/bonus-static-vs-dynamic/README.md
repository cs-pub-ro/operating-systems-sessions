# Solution: make your library — static vs dynamic linking

This is the completed setup for the bonus exercise in [`bonus-static-vs-dynamic`](../../bonus-static-vs-dynamic).

The exercise itself is about running commands and reading their output, not about writing code: `main.c` and the `Makefile` were already provided, and the one step the student performs is copying `mystring.c` / `mystring.h` in from the string-functions exercise. That is what this directory is — the exercise with the reference `mystring.c` already in place, so everything builds out of the box:

```console
make
```

Everything below is what the commands actually produce here, so you can check your own output against it.

## What gets built

| target | how `libmystring` is linked | how libc is linked |
| --- | --- | --- |
| `main_static` | `.a`, copied into the binary | dynamically |
| `main_dynamic` | `.so`, resolved at run time | dynamically |
| `main_fullstatic` | `.a` | statically — everything baked in |

The static library is just `ar rcs libmystring.a mystring.o` — an archive is a bag of `.o` files with an index, closer to a `.tar` than to a program. The shared one needs `-fPIC`, because the `.so` may be mapped at a different address in every process that loads it and so cannot contain hardcoded absolute addresses.

## `make inspect`

```text
=== size ===
   text	   data	    bss	    dec	    hex	filename
   3047	    640	     24	   3711	    e7f	main_static
   3040	    680	     24	   3744	    ea0	main_dynamic
 668981	  23376	  22440	 714797	  ae82d	main_fullstatic
```

`main_fullstatic` is ~180× the text size of the other two: that is libc coming along for the ride.

```text
=== ldd main_static ===
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6
	/lib64/ld-linux-x86-64.so.2
=== ldd main_dynamic ===
	libmystring.so => ./libmystring.so
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6
	/lib64/ld-linux-x86-64.so.2
=== ldd main_fullstatic ===
	not a dynamic executable
```

`main_static` lists only libc — its copy of `my_strlen` is inside the binary. `main_fullstatic` has no loader at all.

```text
=== is my_strlen an undefined symbol? ===
main_static   : (no - it is inside the binary)
main_dynamic  :                  U my_strlen

=== how main calls my_strlen ===
main_static   :     116b:	e8 d0 02 00 00       	call   1440 <my_strlen>
main_dynamic  :     11cb:	e8 00 ff ff ff       	call   10d0 <my_strlen@plt>
```

This is the whole difference in one line each. `main_dynamic` cannot contain the address of `my_strlen` — nobody knows it until `libmystring.so` is mapped — so the compiler emits a call to a local PLT stub that jumps through the GOT to whatever address the loader eventually writes there.

## Running the dynamic build

```console
./main_dynamic 1000
./main_dynamic: error while loading shared libraries: libmystring.so: ...
```

This is expected, and it is the single most common linking error there is. `-L.` told the **linker** where to look at build time; it said nothing to the **loader** at run time, and `.` is deliberately not on the loader's search path. Use `make run-dynamic`, which sets `LD_LIBRARY_PATH=.`, or link with `-Wl,-rpath,'$ORIGIN'`.

## Measuring

```console
make bench      # steady-state call cost
make startup    # process start-up cost
```

Both are timing-sensitive and will differ from machine to machine; the exercise README has reference numbers and the interpretation. The short version: the dynamic build pays one extra indirect jump per call, forever, and that is a small but real and repeatable cost — which is why `make bench` interleaves the binaries and repeats five times instead of trusting a single pair of runs.
