"""
Module 32: xss_csrf_on_toy_browser -- runs both real attack
demonstrations against this course's own toy browser stack.
"""

from csrf_demo import simulate_csrf_attack
from xss_demo import run_xss_demo


def main() -> None:
    print("############################################")
    print("# PART A: Stored XSS against the toy DOM/CSP #")
    print("############################################\n")
    run_xss_demo()

    print("\n\n###########################################")
    print("# PART B: CSRF against a toy bank server   #")
    print("###########################################\n")
    print("=== BEFORE: session cookie has SameSite=None ===\n")
    simulate_csrf_attack(session_same_site="None")
    print("\n" + "-" * 60 + "\n")
    print("=== AFTER: session cookie set with SameSite=Lax ===\n")
    simulate_csrf_attack(session_same_site="Lax")


if __name__ == "__main__":
    main()
