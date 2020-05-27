#if 0
// WIP: shared memory test case handover, requires current afl++ dev branch
__AFL_FUZZ_INIT();
#endif

int
main(void) {
#if 0
  #ifdef __AFL_HAVE_MANUAL_CONTROL
    __AFL_INIT();
  #endif
    while (__AFL_LOOP(100000)) {
    }
#endif

    return 0;
}
