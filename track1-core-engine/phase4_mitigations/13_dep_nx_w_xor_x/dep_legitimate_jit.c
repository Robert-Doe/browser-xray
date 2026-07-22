/*
 * Module 13: dep_nx_w_xor_x -- the sanctioned alternative.
 *
 * Runs the EXACT SAME machine code as dep_violation.c, but obtains its
 * memory the way a real JIT compiler (including a JavaScript engine's
 * JIT, e.g. V8's or SpiderMonkey's) legitimately does: an explicit
 * Win32 call, VirtualAlloc with PAGE_EXECUTE_READWRITE, asking the OS
 * for memory that is genuinely permitted to be executed.
 *
 * This is not "bypassing" DEP -- it's the sanctioned front door DEP
 * was always designed to have. DEP blocks EXECUTING WRITABLE MEMORY
 * THE OS WAS NEVER TOLD WOULD BE CODE. It was never meant to block
 * memory the OS explicitly marked executable on request.
 */
#include <stdio.h>
#include <string.h>
#include <windows.h>

typedef int (*func_ptr)(void);

int main(void) {
    unsigned char code[] = { 0xB8, 0x2A, 0x00, 0x00, 0x00, 0xC3 }; /* mov eax,42; ret */

    void *buffer = VirtualAlloc(NULL, sizeof(code), MEM_COMMIT | MEM_RESERVE,
                                 PAGE_EXECUTE_READWRITE);
    if (!buffer) {
        fprintf(stderr, "VirtualAlloc failed, error %lu\n", GetLastError());
        return 1;
    }
    memcpy(buffer, code, sizeof(code));

    printf("Wrote %zu bytes of the SAME machine code into a VirtualAlloc'd, "
           "PAGE_EXECUTE_READWRITE region at %p\n", sizeof(code), buffer);
    printf("This page was explicitly, deliberately marked executable. Jumping in...\n");
    fflush(stdout);

    func_ptr f = (func_ptr)buffer;
    int result = f();

    printf("Returned cleanly. Result: %d (expected 42)\n", result);

    VirtualFree(buffer, 0, MEM_RELEASE);
    return (result == 42) ? 0 : 2;
}
