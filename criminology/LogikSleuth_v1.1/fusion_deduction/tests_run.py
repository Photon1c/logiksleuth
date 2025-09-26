import sys
from pathlib import Path


def main() -> int:
    pkg_root = Path(__file__).resolve().parent
    if str(pkg_root) not in sys.path:
        sys.path.insert(0, str(pkg_root))
    # Import tests and run simple assertions
    from tests.test_elimination import test_filter_candidates
    from tests.test_deduction import test_update_posterior_yes_no
    from tests.test_rules import test_handle_question, test_handle_probe_and_accuse

    test_filter_candidates()
    test_update_posterior_yes_no()
    test_handle_question()
    test_handle_probe_and_accuse()
    print("All tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

