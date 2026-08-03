# -g  : keep debug symbols, so gdb and Valgrind can show source lines
# -O0 : no optimisations, so the code you step through is the code you wrote
CC = gcc
CFLAGS = -Wall -Wextra -g -O0

# Default target: build the program you have to debug.
histogram: main.c
	$(CC) $(CFLAGS) -o histogram main.c

# `make sol`: build the reference solution.
sol: solution.c
	$(CC) $(CFLAGS) -o histogram-sol solution.c

clean:
	rm -f histogram histogram-sol

.PHONY: sol clean
