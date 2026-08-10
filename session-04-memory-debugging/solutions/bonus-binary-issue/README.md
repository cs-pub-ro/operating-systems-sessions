# Solution: binary patching a buffer overflow

This is the reference solution for the bonus binary-patching exercise.
If you were sent here from `bonus-binary-issue/`, this directory shows the source code the shipped binary was built from, and a working patcher — try to find and fix the bug yourself first, working only from the binary.

## What it is

`vuln.c` is a tiny program that greets the user, reads one line of input into a fixed-size stack buffer, and prints it back:

```c
static void reader(void)
{
	char buffer[64];

	printf("gimme message: ");
	fgets(buffer, 128, stdin);
	printf("hello, %s\n", buffer);
}
```

The bug is on the `fgets()` line: `buffer` is 64 bytes, but `fgets()` is told it may write up to 128.
Any line of input 64 bytes or longer overflows `buffer[]` and overwrites whatever the compiler placed right after it on the stack.

The binary is built with `-fno-stack-protector -no-pie` specifically so that this overflow reaches the saved return address instead of being caught by a stack canary, and so that addresses are fixed instead of randomised — both purely to make the bug reliably reproducible for a classroom demo.
Also note `vuln.c` contains a few unused static functions (`warcraft`, `diablo`, `starcraft`) and a global (`g`) that nothing calls or reads from `main()`.
They are not part of this bug; they exist as red herrings / bonus material for students who go looking at the binary's full symbol table with `nm` or `objdump -t` and wonder what else is in there.

## Build, run, test

```console
make          # builds ./vuln exactly as shipped to students (no -g)
make debug    # builds ./vuln-debug, same source, with debug info
make patch    # builds ./vuln, then produces ./vuln.patched via patch_vuln.py
make test     # builds everything and demonstrates bug + fix end-to-end
```

`make test` output looks like this:

```text
== 1. vuln, short input (expected: prints back the string) ==
hello, blizzard!
gimme message: hello, hello

== 2. vuln, long input (expected: segmentation fault) ==
Segmentation fault (core dumped)
exit status: 139

== 3. vuln.patched, long input (expected: no crash, truncated output) ==
hello, blizzard!
gimme message: hello, AAAA...AAAA
exit status: 0

all good: vuln crashes on long input, vuln.patched does not.
```

You can reproduce the crash and inspect it with gdb (this build has no `-g`, so `bt` will not have file/line info, but with `vuln-debug` it will):

```console
python3 -c "print('A' * 100)" > /tmp/overflow.txt
gdb ./vuln-debug
(gdb) run < /tmp/overflow.txt
```

```text
Program received signal SIGSEGV, Segmentation fault.
0x000000000040124b in reader () at vuln.c:30
(gdb) bt
#0  0x000000000040124b in reader () at vuln.c:30
#1  0x4141414141414141 in ?? ()
```

The saved return address is `0x4141414141414141` — eight `'A'` bytes from the input.
That is the fingerprint of a classic stack-smashing buffer overflow: the overwritten data is not "corrupted" in some complicated way, it is *literally the attacker's input*, sitting where the return address used to be.

## Finding the bug from the binary alone

Since the shipped binary has no debug info, the workflow is: disassemble, find the function that reads input, and look at the size argument passed to whatever function writes into the buffer.

```console
objdump -d --disassemble=reader -M intel vuln
```

```text
00000000004011f6 <reader>:
  ...
  401216:  mov    rdx,QWORD PTR [rip+0x2e13]   # stdin
  40121d:  lea    rax,[rbp-0x40]
  401221:  mov    esi,0x80                     ; <-- size argument: 128 (0x80)
  401226:  mov    rdi,rax
  401229:  call   401080 <fgets@plt>
```

`lea rax,[rbp-0x40]` computes the address of a 64-byte (`0x40`) region on the stack — that is `buffer`.
But the very next instruction loads `0x80` (128) into `esi`, the register that holds `fgets()`'s second argument (its maximum size).
`0x80 != 0x40`: the size passed to `fgets()` is twice the real size of the buffer it is writing into.

## The fix: patch the machine code, not the source

`patch_vuln.py` finds the byte pattern for `mov esi, 0x80` (opcode `0xBE` followed by the little-endian 32-bit immediate `0x80 0x00 0x00 0x00`), confirms it precedes a `call` instruction (so it does not patch an unrelated coincidental match), and overwrites the immediate with `0x40` (64):

```console
python3 patch_vuln.py vuln -o vuln.patched
```

```text
found buggy instruction at file offset 0x1221: mov esi, 128
patched immediate at file offset 0x1222: mov esi, 128 -> mov esi, 64
wrote patched binary to vuln.patched
```

Confirm with `objdump` that only that one instruction changed:

```console
objdump -d --disassemble=reader -M intel vuln.patched
```

```text
  401221:  be 40 00 00 00       mov    esi,0x40
```

Four bytes changed in a 16-kilobyte file, and the vulnerability is gone — `fgets()` now cannot write past the end of `buffer[]`.

## Why patch the binary instead of just fixing vuln.c and recompiling?

Recompiling is obviously the right fix when you have the source.
This exercise is about the situation where you do **not**: a vendor-supplied binary, a legacy build with no surviving source tree, a binary you are auditing that you did not write.
Being able to go from "I found a bug by reading disassembly" to "I fixed the bug by changing four bytes, verifiably and minimally" without rebuilding anything is a real skill — it is exactly what a binary patch/hotfix, a hex-edit of a firmware image, or a hand-written disassembler-guided exploit mitigation looks like in practice.
