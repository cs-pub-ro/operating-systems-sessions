# Exercise: the program that is right and still broken

`main.c` reads words from standard input and reports how many there were and which one was the longest.
The answer it prints is correct, it never crashes, and `-Wall -Wextra` says nothing.

## Reproduce

```console
make
valgrind --leak-check=full ./longest < input.txt
```

The program keeps exactly one string on the heap — the longest word seen so far — and `main()` frees it at the end.
Valgrind still reports bytes *definitely lost*, which means that at exit no pointer to that memory existed anywhere.

## Your tasks

1. Find the leak.
   Count how many words in the input are longer than every word before them: that is how many heap copies the program makes.
   A pointer variable holds one address, so ask what happens to the address that was in it when a new one is assigned on top.
1. Fix it, keeping the output identical.
   The struct owns the string it points to, so the old string has to be released before the pointer is overwritten.
1. Check your work, corner cases included:

    ```console
    valgrind --leak-check=full ./longest < input.txt
    printf 'aaa\n' | ./longest
    printf '' | ./longest
    printf 'zz\naaa\nbbbb\naaaaa\n' | ./longest
    ```

Every run must end at `All heap blocks were freed` with 0 errors.
`free(NULL)` is legal and does nothing, so the empty input needs no special case — but freeing the same pointer twice is undefined behaviour, and Valgrind reports it as an invalid free.
