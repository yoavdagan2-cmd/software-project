"""
Standalone tester for the C extension `mykmeanssp`.

It does NOT need kmeans_pp.py. It:
  1. builds the extension (python3 setup.py build_ext --inplace),
  2. imports mykmeanssp,
  3. for each case: joins the two db files, runs kmeans++ init (seed 1234,
     Euclidean distance) to get the initial centroids,
  4. calls mykmeanssp.fit(...) and compares the returned centroids (and the
     chosen initial indices) against the expected output_*.txt files.

Run:  python3 test_c_module.py [tests_folder]
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_arg = sys.argv[1] if len(sys.argv) > 1 else "tests-2"
TESTS_DIR = _arg if os.path.isabs(_arg) else os.path.join(BASE_DIR, _arg)

# (k, iter, eps, file1, file2, expected_output)
CASES = [
    (3,  333, 0.0, "input_1_db_1.txt", "input_1_db_2.txt", "output_1.txt"),
    (7,  300, 0.0, "input_2_db_1.txt", "input_2_db_2.txt", "output_2.txt"),
    (15, 350, 0.0, "input_3_db_1.txt", "input_3_db_2.txt", "output_3.txt"),
]

TOL = 1e-4


def build_extension():
    print(">> building extension: python3 setup.py build_ext --inplace")
    proc = subprocess.run(
        [sys.executable, "setup.py", "build_ext", "--inplace"],
        cwd=BASE_DIR, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print("BUILD FAILED:\n" + (proc.stderr or proc.stdout))
        sys.exit(2)
    print(">> build ok\n")


def p(name):
    return os.path.join(TESTS_DIR, name)


def read_db(path):
    """key (int) -> list of float features, from a 'key,f1,f2,...' file."""
    table = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            key = int(round(float(parts[0])))
            table[key] = [float(x) for x in parts[1:]]
    return table


def load_and_combine(f1, f2):
    """Inner-join on key, sort ascending by key. Returns (keys, data)."""
    import numpy as np
    a = read_db(f1)
    b = read_db(f2)
    keys = sorted(set(a) & set(b))
    data = np.array([a[k] + b[k] for k in keys], dtype=float)
    return keys, data


def kmeans_pp_init(data, k):
    """Algorithm 1 (kmeans++). seed 1234, np.random.choice, Euclidean D.
    Returns the list of chosen row indices."""
    import numpy as np
    np.random.seed(1234)
    n = data.shape[0]
    chosen = [int(np.random.choice(n))]
    d = np.sqrt(np.sum((data - data[chosen[0]]) ** 2, axis=1))
    for _ in range(1, k):
        probs = d / d.sum()
        nxt = int(np.random.choice(n, p=probs))
        chosen.append(nxt)
        d = np.minimum(d, np.sqrt(np.sum((data - data[nxt]) ** 2, axis=1)))
    return chosen


def read_expected(path):
    with open(path) as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]
    idx_line = lines[0]
    centroids = [[float(x) for x in ln.split(",")] for ln in lines[1:]]
    return idx_line, centroids


def main():
    if not os.path.isdir(TESTS_DIR):
        print(f"Tests folder not found: {TESTS_DIR}")
        sys.exit(2)

    build_extension()

    try:
        import mykmeanssp
    except ImportError as e:
        print("Could not import mykmeanssp after build:", e)
        sys.exit(2)
    try:
        import numpy  # noqa: F401
    except ImportError:
        print("numpy is required to run this tester (pip install numpy).")
        sys.exit(2)

    all_ok = True
    for k, it, eps, f1, f2, expfile in CASES:
        label = f"k={k}, iter={it}, eps={eps}, {f1}+{f2}"
        keys, data = load_and_combine(p(f1), p(f2))

        chosen = kmeans_pp_init(data, k)
        init_centroids = data[chosen].tolist()

        result = mykmeanssp.fit(init_centroids, data.tolist(), k, it, eps)

        exp_idx, exp_centroids = read_expected(p(expfile))
        got_idx = ",".join(str(keys[i]) for i in chosen)

        ok = True
        detail = ""

        if got_idx != exp_idx:
            ok = False
            detail = f"initial indices differ:\n     got:      {got_idx}\n     expected: {exp_idx}"

        if ok:
            if len(result) != len(exp_centroids):
                ok = False
                detail = f"centroid count: got {len(result)}, expected {len(exp_centroids)}"
            else:
                for i, (gr, er) in enumerate(zip(result, exp_centroids)):
                    for gv, ev in zip(gr, er):
                        if abs(gv - ev) > TOL:
                            ok = False
                            detail = f"centroid line {i}: {gv:.4f} != {ev:.4f}"
                            break
                    if not ok:
                        break

        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
        if not ok:
            print("   ", detail)
            all_ok = False

    print()
    print("ALL TESTS PASSED" if all_ok else "SOME TESTS FAILED")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
