# Stream Ciphers: Caesar & Vigenere

## Overview

This exercise presents two classical stream ciphers:

* **Caesar cipher** — shifts every letter in the input by a fixed integer offset.
* **Vigenere cipher** — shifts each letter by the value of the corresponding character in a repeating key.

The implementation is already there, in the `cipher.c` and `vigenere.c` source code files, respectively: the functions `caesar()` and `vigenere()`.
The function signatures are part of the `caesar.h` and `vigenere.h` header files.
The `main.c` file contains the `main()` function that includes the `caesar.h` and `vigenere.h` header files, and calls the `caesar()` and `vigenere()` functions.

Find below instructions to build the program in multiple formats:

1. a dynamicall-linked executable
1. a statically-linked executable
1. a shared library + a dynamically-linked executable
1. a static library + a statically-linked executable

## Build

Use the commands below to build the various types of executables.

### 1. Dynamically-linked executable (all sources compiled together)

```console
gcc -Wall -o cipher main.c caesar.c vigenere.c
```

### 2. Statically-linked executable

```console
gcc -Wall -static -o cipher-static main.c caesar.c vigenere.c
```

### 3. Shared library + dynamically-linked executable

```console
# Build the shared library
gcc -Wall -fPIC -shared -o libcipher.so caesar.c vigenere.c

# Link main.c against the shared library
gcc -Wall -o cipher-dyn main.c -L. -lcipher

# Run (tell the loader where to find libcipher.so)
LD_LIBRARY_PATH=. ./cipher-dyn caesar 3 "Hello, World!"
```

### 4. Static library + statically-linked executable

```console
# Compile object files
gcc -Wall -c -o caesar.o caesar.c
gcc -Wall -c -o vigenere.o vigenere.c

# Archive into a static library
ar rcs libcipher.a caesar.o vigenere.o

# Link main.c against the static library
gcc -Wall -o cipher-static-lib main.c -L. -lcipher -static

# Run
./cipher-static-lib caesar 3 "Hello, World!"
```

## Run

Use the commands below to run the executables.
All executables, irrespective of the format, will run the same way, with the same type of arguments

```console
./cipher caesar  <shift>  <text>
./cipher vigenere <key>   <text>
```

| Argument | Description |
|----------|-------------|
| `shift`  | Integer offset; positive = encrypt, negative = decrypt |
| `key`    | Letters only (case-insensitive), used as the Vigenere key |
| `text`   | The string to process (quote it if it contains spaces) |

### Examples

```console
# Caesar encrypt
$ ./cipher caesar 3 "Hello, World!"
Khoor, Zruog!

# Caesar decrypt
$ ./cipher caesar -3 "Khoor, Zruog!"
Hello, World!

# Vigenere encrypt
$ ./cipher vigenere key "Hello, World!"
Rijvs, Uyvjn!

# Vigenere decrypt (apply the same key to the ciphertext)
$ ./cipher vigenere key "Rijvs, Uyvjn!"
Hello, World!
```

## How the Ciphers Work

### Caesar

Each letter is shifted by a constant `shift` (mod 26).
Non-letter characters are left unchanged.

```text
encrypt: C = (P + shift) mod 26
decrypt: P = (C - shift) mod 26
```

### Vigenere

The key is repeated to match the length of the plaintext (skipping non-letters).
Each letter is shifted by the alphabetic index of the corresponding key character.

```text
encrypt: C_i = (P_i + K_{i mod len(key)}) mod 26
decrypt: P_i = (C_i - K_{i mod len(key)} + 26) mod 26
```

Because the same operation applied twice with the same key returns the original text (the shifts cancel mod 26), decryption is simply running the program again with the same key.
