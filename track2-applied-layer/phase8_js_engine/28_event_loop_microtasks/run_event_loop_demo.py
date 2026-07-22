"""
Module 28: event_loop_microtasks -- demonstration runner.

Simulates the real, classic JS ordering scenario:

    console.log('script start');
    setTimeout(() => console.log('setTimeout 1'), 0);
    Promise.resolve().then(() => console.log('promise 1'));
    setTimeout(() => console.log('setTimeout 2'), 0);
    Promise.resolve().then(() => {
      console.log('promise 2');
      Promise.resolve().then(() => console.log('promise 3'));
    });
    console.log('script end');

Real JS's well-known, correct output order is:
    script start, script end, promise 1, promise 2, promise 3,
    setTimeout 1, setTimeout 2

`setTimeout`, even with a 0ms delay, is a MACROTASK -- it never runs
before the current script's synchronous code finishes, and never
before the microtask queue is fully drained. `Promise.resolve().then()`
is a MICROTASK -- including the ones (promise 3) queued from INSIDE
another already-running microtask (promise 2).
"""

from event_loop import EventLoop


def main() -> None:
    loop = EventLoop()

    # --- "synchronous" top-level script code ---
    loop.log.append("sync: script start")

    loop.queue_macrotask(lambda: loop.log.append("macrotask body: setTimeout 1"), "setTimeout 1")

    loop.queue_microtask(lambda: loop.log.append("microtask body: promise 1"), "promise 1")

    loop.queue_macrotask(lambda: loop.log.append("macrotask body: setTimeout 2"), "setTimeout 2")

    def promise_2_callback():
        loop.log.append("microtask body: promise 2")
        # This microtask queues ANOTHER microtask WHILE the microtask
        # queue is still being drained -- the real rule says it still
        # runs before the NEXT macrotask, not after.
        loop.queue_microtask(lambda: loop.log.append("microtask body: promise 3"), "promise 3")

    loop.queue_microtask(promise_2_callback, "promise 2")

    loop.log.append("sync: script end")

    # --- event loop takes over ---
    loop.run()

    print("Actual execution order:\n")
    for i, entry in enumerate(loop.log, start=1):
        print(f"  {i}. {entry}")

    expected_order = [
        "sync: script start",
        "sync: script end",
        "microtask: promise 1",
        "microtask body: promise 1",
        "microtask: promise 2",
        "microtask body: promise 2",
        "microtask: promise 3",
        "microtask body: promise 3",
        "macrotask: setTimeout 1",
        "macrotask body: setTimeout 1",
        "macrotask: setTimeout 2",
        "macrotask body: setTimeout 2",
    ]
    print(f"\nMatches real JS's well-known ordering? {loop.log == expected_order}")


if __name__ == "__main__":
    main()
