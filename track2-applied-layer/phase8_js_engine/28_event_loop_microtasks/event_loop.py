"""
Module 28: event_loop_microtasks -- a real, working toy event loop.

The one rule this module exists to prove, experimentally: after EVERY
macrotask finishes running, the ENTIRE microtask queue is drained --
completely, including any new microtasks queued DURING that draining
-- before the next macrotask is even considered. This is not a minor
implementation detail; it's the exact mechanism that makes
Promise-based code (microtasks) consistently run before setTimeout-based
code (macrotasks), even when both are queued at the "same time."

SCOPE (see DECISIONS.md): this models the browser/Node event loop's
task-queue SHAPE -- it does not implement real timers, real I/O, or
real Promise objects. Callbacks are plain Python callables, queued
directly via this module's own API.
"""

from collections import deque


class EventLoop:
    def __init__(self):
        self.macrotasks = deque()
        self.microtasks = deque()
        self.log: list = []

    def queue_macrotask(self, callback, label: str) -> None:
        self.macrotasks.append((callback, label))

    def queue_microtask(self, callback, label: str) -> None:
        self.microtasks.append((callback, label))

    def _drain_microtasks(self) -> None:
        """Runs EVERY currently-queued microtask to completion --
        including ones queued by microtasks that ran moments ago
        during this SAME drain. This full-drain behavior (not just
        "run whatever was queued when we started") is exactly the real
        rule; see Module 28's DECISIONS.md for the deliberate test case
        proving it."""
        while self.microtasks:
            callback, label = self.microtasks.popleft()
            self.log.append(f"microtask: {label}")
            callback()

    def run(self) -> None:
        """Call this AFTER whatever counts as this script's own
        top-level "synchronous" code has already run directly (see
        run_script_demo.py) -- draining any microtasks that
        synchronous code queued, then processing macrotasks one at a
        time, fully draining microtasks after each one."""
        self._drain_microtasks()
        while self.macrotasks:
            callback, label = self.macrotasks.popleft()
            self.log.append(f"macrotask: {label}")
            callback()
            self._drain_microtasks()
