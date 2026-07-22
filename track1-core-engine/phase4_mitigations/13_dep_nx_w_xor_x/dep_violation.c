/*
 * Module 13: dep_nx_w_xor_x -- the violation.
 *
 * Writes a tiny, real, valid piece of x86-64 machine code -- the
 * complete function "return 42;" hand-assembled to raw bytes -- into
 * ordinary heap memory obtained from malloc(), then jumps into it as
 * if it were a function.
 *
 * Ordinary heap memory is READ+WRITE, never EXECUTE. On any modern
 * 64-bit Windows process, DEP/NX enforcement is a permanent hardware
 * property of 64-bit code -- there is no per-process opt-out the way
 * there historically was on 32-bit Windows. This program is expected
 * to CRASH. That crash, not a clean exit, is the actual proof.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int (*func_ptr)(void);

int main(void) {
    /* Machine code for: mov eax, 42 ; ret
       B8 2A 00 00 00       mov eax, 0x2A (42)
       C3                   ret                                    */
    unsigned char code[] = { 0xB8, 0x2A, 0x00, 0x00, 0x00, 0xC3 };

    unsigned char *buffer = malloc(sizeof(code));
    if (!buffer) {
        fprintf(stderr, "malloc failed\n");
        return 1;
    }
    memcpy(buffer, code, sizeof(code));

    printf("Wrote %zu bytes of real machine code into a malloc'd heap buffer at %p\n",
           sizeof(code), (void *)buffer);
    printf("Heap memory is READ+WRITE, never EXECUTE. Jumping into it now...\n");
    fflush(stdout);

    func_ptr f = (func_ptr)buffer;
    int result = f();  /* <-- expected to crash here, not return */

    /* If we ever reach this line, DEP did not do its job. */
    printf("UNREACHABLE: heap-resident code executed and returned %d\n", result);

    free(buffer);
    return 0;
}
