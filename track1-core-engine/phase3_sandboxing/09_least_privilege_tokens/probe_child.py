"""
Module 9: least_privilege_tokens -- the child under test.

A tiny probe: given a file path and a mode ("read" or "write"),
attempts exactly that one operation and reports plainly whether it
succeeded or failed. Run under different tokens by the orchestrator to
see how the SAME code, against the SAME file, behaves differently
purely as a function of the token it's running under.
"""

import sys


def main() -> None:
    path = sys.argv[1]
    mode = sys.argv[2]
    try:
        if mode == "read":
            with open(path, "r") as f:
                content = f.read().strip()
            print(f"READ OK: {content!r}")
        elif mode == "write":
            with open(path, "a") as f:
                f.write("appended by probe_child.py\n")
            print("WRITE OK")
        else:
            raise ValueError(f"unknown mode {mode!r}")
    except PermissionError as e:
        print(f"{mode.upper()} FAILED: PermissionError: {e}")


if __name__ == "__main__":
    main()
