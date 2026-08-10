# Stream Ciphers: Caesar & Vigenere: Per-Cipher Executable

In exercise `03-stream-cipher` we created an executable that used both the Caesar and the Vigenere cipher.
We want an executable dedicated to using the Caesar cipher, and another executable dedicated to using the Vigenere cipher.

Based on the commands used in exercise `03-stream-cipher`, create a specific executable for each type of cipher (Caesar or Vigenere).
Similarly, build all four formats of executables for each cipher.

That means you will:

1. Create a `caesar_main.c` source code file to use the Caesar cipher implementation.
   The file includes the `caesar.h` header and calls the `caesar()` function.
   You can create a copy of the `main.c` source code file from the `03-stream-cipher/` directory and remove the parts that refers the Vigenere cipher implementation.
   The program will only receive two command line arguments: the shift and the key.
   The first command line argument used in the `main.c` file was the cipher name;
   that argument is no longer relevant, since the program only uses one cipher.

1. Create a `vigenere_main.c` source code file to use the Vigenere cipher implementation.
   The file includes the `vigenere.h` header and calls the `vigenere()` function.
   You can create a copy of the `main.c` source code file and remove the parts that refers the Caesar cipher implementation.
   The program will only receive two command line arguments: the shift and the key.
   The first command line argument used in the `main.c` file was the cipher name;
   that argument is no longer relevant, since the program only uses one cipher.

1. Build the executable that uses the Caesar cipher in the four formats above.
   Build it from the `caesar_main.c` and the `caesar.c` source code files.
   The executables will be named `caesar`, `caesar-static`, `caesar-dyn`, `caesar-static-lib`.
   The library files will only include the `caesar.o` object file.

1. Build the executable that uses the Vigenere cipher in the four formats above.
   Build it from the `vigenere_main.c` and the `vigenere.c` source code files.
   The executables will be named `vigenere`, `vigenere-static`, `vigenere-dyn`, `vigenere-static-lib`.
   The library files will only include the `vigenere.o` object file.

After building the 8 executables, run them and see if everything works OK.
