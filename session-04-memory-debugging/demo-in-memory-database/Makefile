# -g  : keep debug symbols, so gdb and Valgrind can show source lines
# -O0 : no optimisations, so the code you step through is the code you wrote
CC = gcc
CFLAGS = -Wall -Wextra -g -O0

# Default target: build the buggy program we are going to debug.
db: main.c
	$(CC) $(CFLAGS) -o db main.c

# `make sol`: build the fixed version.
sol: solution.c
	$(CC) $(CFLAGS) -o db-sol solution.c

clean:
	rm -f db db-sol

.PHONY: sol clean
