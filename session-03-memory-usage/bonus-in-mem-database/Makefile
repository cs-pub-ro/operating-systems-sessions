CC = gcc
CFLAGS = -Wall -Wextra

# Default target: build the skeleton (copy your task-1 main.c here first).
db: main.c
	$(CC) $(CFLAGS) -o db main.c

# `make sol`: build the reference solution.
sol: solution.c
	$(CC) $(CFLAGS) -o db-sol solution.c

clean:
	rm -f db db-sol

.PHONY: sol clean
