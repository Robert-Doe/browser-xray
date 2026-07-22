"""
Module 7: shared_memory -- orchestrates the full experiment.

Part A: writer and reader agree on the SAME tagname -- real, live,
bidirectional sharing: the reader sees the writer's data with no
message-passing, then writes its own value back, and the still-running
writer sees THAT too.

Part B: writer and reader use DIFFERENT tagnames (a stand-in for a
typo, or two components that were never actually configured to agree).
Unlike Module 6's pipes/sockets, this does NOT raise an error -- it
silently produces two independent, unrelated segments. This is the
real, easy-to-miss failure mode shared memory has that message-passing
IPC does not.
"""

import subprocess
import sys
import time

WRITER_TAG = "Local\\module7_shared_demo"
WRONG_TAG = "Local\\module7_shared_demo_TYPO"


def part_a_real_sharing() -> None:
    print("=== Part A: writer and reader agree on the same tagname ===\n")
    writer = subprocess.Popen(
        [sys.executable, "shared_writer.py", WRITER_TAG, "hello from the writer"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    time.sleep(0.4)  # let the writer create the segment and write before we read it

    reader = subprocess.run(
        [sys.executable, "shared_reader.py", WRITER_TAG, "hello back from the reader"],
        capture_output=True,
        text=True,
        check=True,
    )
    print(reader.stdout)

    writer.stdin.write("\n")  # unblock the writer's stdin.readline()
    writer.stdin.close()
    writer_out, _ = writer.communicate(timeout=5)
    print(writer_out)


def part_b_mismatched_tagname() -> None:
    print("=== Part B: writer and reader use DIFFERENT tagnames (a typo) ===\n")
    writer = subprocess.Popen(
        [sys.executable, "shared_writer.py", WRITER_TAG, "hello from the writer"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    time.sleep(0.4)

    reader = subprocess.run(
        [sys.executable, "shared_reader.py", WRONG_TAG],
        capture_output=True,
        text=True,
        check=True,
    )
    print(reader.stdout)
    print(
        "[analysis] the reader did NOT see the writer's string, and got NO "
        "error -- it silently mapped its own separate, zero-filled segment "
        "under the mismatched name. Compare this to Module 6, where a "
        "mismatched pipe name or port failed loudly instead."
    )

    writer.stdin.write("\n")
    writer.stdin.close()
    writer_out, _ = writer.communicate(timeout=5)
    print(writer_out)


def main() -> None:
    part_a_real_sharing()
    part_b_mismatched_tagname()


if __name__ == "__main__":
    main()
