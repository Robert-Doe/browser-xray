/*
 * Module 14: stack_canaries_cfi -- a REAL, genuine stack buffer
 * overflow (unlike Module 13, which jumped into deliberately-placed
 * bytes -- this program has an actual memory-safety BUG).
 *
 * vulnerable() copies its argument into a fixed 16-byte stack buffer
 * using strcpy -- no length check at all. Passed a long enough
 * string, strcpy will keep writing straight past the end of `buf`,
 * into whatever the compiler placed adjacent to it on the stack --
 * which, depending on how this file is compiled, may include a stack
 * canary value and/or the saved return address itself.
 *
 * This file is compiled TWICE by run_canary_demo.py: once with GCC's
 * stack protector enabled (the default), once with it explicitly
 * disabled -- to show exactly what the canary catches, and what
 * happens to identical vulnerable code without it.
 */
#include <stdio.h>
#include <string.h>

void vulnerable(const char *input) {
    char buf[16];
    printf("  buf is at a fixed 16-byte stack slot; input is %zu bytes\n", strlen(input));
    strcpy(buf, input);  /* THE BUG: no bounds check whatsoever */
    printf("  strcpy completed. buf now contains: %s\n", buf);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <string>\n", argv[0]);
        return 1;
    }
    printf("Calling vulnerable() with an argument %zu bytes long...\n", strlen(argv[1]));
    fflush(stdout);

    vulnerable(argv[1]);

    /* Reaching this line at all means the function returned normally
       -- i.e. whatever strcpy overwrote did not corrupt anything that
       mattered for returning control here cleanly. */
    printf("vulnerable() returned normally. No corruption reached anything critical.\n");
    return 0;
}
