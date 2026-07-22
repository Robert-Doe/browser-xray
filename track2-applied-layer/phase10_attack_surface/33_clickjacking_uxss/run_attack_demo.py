"""
Module 33: clickjacking_uxss -- runs both real attack demonstrations.
"""

from clickjacking_demo import main as run_clickjacking_demo
from uxss_demo import main as run_uxss_demo


def main() -> None:
    print("###############################################")
    print("# PART A: Clickjacking -- the compositor gap   #")
    print("###############################################\n")
    run_clickjacking_demo()

    print("\n\n###############################################")
    print("# PART B: UXSS -- the site-isolation gap       #")
    print("###############################################\n")
    run_uxss_demo()


if __name__ == "__main__":
    main()
