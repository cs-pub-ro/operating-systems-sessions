CC = gcc
CFLAGS = -Wall -Wextra

# Default target: build the skeleton the students complete.
db: main.c
	$(CC) $(CFLAGS) -o db main.c

# `make sol`: build the reference solution.
sol: solution.c
	$(CC) $(CFLAGS) -o db-sol solution.c

clean:
	rm -f db db-sol

.PHONY: sol clean
