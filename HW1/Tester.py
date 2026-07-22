"""
Test harness for HW1 kmeans.py.

Runs kmeans.py on each test case with its own (K, iter) arguments,
feeding the input file on stdin, and compares the produced output
against the expected output file using EXACT text matching.

Usage:
    python3 run_tests.py

Edit TEST_CASES below to match your files and arguments.
Place this script, your kmeans.py, the input files, and the expected
output files in known locations (paths are configurable below).
"""

import subprocess
import sys
import os

# ---------------------------------------------------------------------------
# CONFIGURE THESE
# ---------------------------------------------------------------------------

# Path to the program under test.
KMEANS = "kmeans.py"

# One entry per test case. Each has its own K / iter (iter optional -> None).
#   input:    the input data file (fed on stdin)
#   expected: the expected output file to compare against
#   k, iter:  command-line arguments (iter=None means "don't pass iter")
TEST_CASES = [
    {"input": "input_1.txt", "expected": "output_1.txt", "k": 3,  "iter": 600},
    {"input": "input_2.txt", "expected": "output_2.txt", "k": 7,  "iter": None},
    {"input": "input_3.txt", "expected": "output_3.txt", "k": 15,  "iter": 300},
]

# ---------------------------------------------------------------------------
# Harness (usually no need to edit below)
# ---------------------------------------------------------------------------

# ANSI colors (fall back to plain if not a TTY)
if sys.stdout.isatty():
    GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
else:
    GREEN = RED = YELLOW = DIM = RESET = ""


def run_one(case):
    """Run kmeans.py for one case. Returns (passed: bool, message: str)."""
    inp = case["input"]
    expected_path = case["expected"]
    k = case["k"]
    it = case["iter"]

    # Build the argument list, matching: python3 kmeans.py K [iter] < input
    args = [sys.executable, KMEANS, str(k)]
    if it is not None:
        args.append(str(it))

    # Sanity: files must exist
    for path in (KMEANS, inp, expected_path):
        if not os.path.exists(path):
            return False, f"missing file: {path}"

    # Feed the input file on stdin, capture stdout.
    with open(inp, "r") as fin:
        try:
            result = subprocess.run(
                args,
                stdin=fin,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            return False, "TIMEOUT (>60s) — possible infinite loop"

    produced = result.stdout

    # If the program crashed / exited non-zero, surface that.
    if result.returncode != 0:
        stderr_tail = result.stderr.strip().splitlines()[-3:]
        return False, (f"exit code {result.returncode}; "
                       f"stderr: {' | '.join(stderr_tail) if stderr_tail else '(none)'}")

    with open(expected_path, "r") as f:
        expected = f.read()

    # EXACT text match.
    if produced == expected:
        return True, "exact match"

    # Not equal — produce a helpful line-by-line diff.
    return False, diff_report(produced, expected)


def diff_report(produced, expected):
    """Build a readable first-difference report between two texts."""
    prod_lines = produced.splitlines()
    exp_lines = expected.splitlines()

    lines = []
    lines.append(f"MISMATCH — produced {len(prod_lines)} lines, "
                 f"expected {len(exp_lines)} lines")

    max_len = max(len(prod_lines), len(exp_lines))
    shown = 0
    for i in range(max_len):
        p = prod_lines[i] if i < len(prod_lines) else "<no line>"
        e = exp_lines[i] if i < len(exp_lines) else "<no line>"
        if p != e:
            lines.append(f"  line {i + 1}:")
            lines.append(f"    expected: {e}")
            lines.append(f"    got:      {p}")
            shown += 1
            if shown >= 5:  # don't flood — first 5 differing lines
                remaining = sum(
                    1 for j in range(i + 1, max_len)
                    if (prod_lines[j] if j < len(prod_lines) else None)
                    != (exp_lines[j] if j < len(exp_lines) else None)
                )
                if remaining:
                    lines.append(f"    ... and {remaining} more differing line(s)")
                break
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("HW1 kmeans.py — test harness (exact match)")
    print("=" * 60)

    passed = 0
    for idx, case in enumerate(TEST_CASES, start=1):
        arg_str = f"K={case['k']}" + (f" iter={case['iter']}" if case["iter"] is not None else " iter=<default>")
        label = f"Test {idx}: {case['input']}  ({arg_str})"
        ok, msg = run_one(case)
        if ok:
            print(f"{GREEN}PASS{RESET}  {label}")
            passed += 1
        else:
            print(f"{RED}FAIL{RESET}  {label}")
            for line in msg.splitlines():
                print(f"      {DIM}{line}{RESET}")
        print()

    print("=" * 60)
    total = len(TEST_CASES)
    color = GREEN if passed == total else (YELLOW if passed else RED)
    print(f"{color}{passed}/{total} passed{RESET}")
    print("=" * 60)

    # Exit non-zero if any failed (handy for scripting)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()