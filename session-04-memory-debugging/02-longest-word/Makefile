# -g  : keep debug symbols, so gdb and Valgrind can show source lines
# -O0 : no optimisations, so the code you step through is the code you wrote
CC = gcc
CFLAGS = -Wall -Wextra -g -O0

# Default target: build the program you have to debug.
longest: main.c
	$(CC) $(CFLAGS) -o longest main.c

# `make sol`: build the reference solution.
sol: solution.c
	$(CC) $(CFLAGS) -o longest-sol solution.c

clean:
	rm -f longest longest-sol

.PHONY: sol clean
