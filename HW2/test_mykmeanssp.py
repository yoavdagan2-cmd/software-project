"""
Test harness for the mykmeanssp C extension (tests fit() only).

Build first, then run (needs input_1.txt / input_2.txt / input_3.txt in the folder):
    python3 setup.py build_ext --inplace
    python3 test_mykmeanssp.py

This checks that your C K-means loop is correct and handles the real datasets.
It does NOT reproduce the official output_*.txt files -- that requires the
kmeans++ initialization, which lives in kmeans_pp.py (not tested here).

fit() signature assumed:  mykmeanssp.fit(centroids, datapoints, k, iter, eps)
"""

import mykmeanssp


def approx_equal(a, b, tol=1e-4):
    return abs(a - b) <= tol


def load_points(path):
    pts = []
    for line in open(path):
        line = line.strip()
        if line:
            pts.append([float(x) for x in line.split(",")])
    return pts


passed = 0
total = 0


# =====================================================================
# PART A: tiny hand-checkable cases (is the algorithm CORRECT?)
# =====================================================================
print("=== PART A: correctness on tiny inputs ===\n")

# A1: two separated clusters, k=2 -> centroids must be the cluster means
data = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0],
        [10.0, 10.0], [10.0, 11.0], [11.0, 10.0]]
init = [[0.0, 0.0], [10.0, 10.0]]
res = mykmeanssp.fit(init, data, 2, 300, 0.0)
exp = [[1.0/3, 1.0/3], [10.0+1.0/3, 10.0+1.0/3]]
total += 1
ok = all(approx_equal(res[i][j], exp[i][j]) for i in range(2) for j in range(2))
print("A1 two clusters      :", "PASS" if ok else "FAIL",
      "  got", [["%.4f" % x for x in r] for r in res])
passed += ok

# A2: already-converged input -> centroids must not move
data = [[0.0, 0.0], [2.0, 2.0]]
init = [[0.0, 0.0], [2.0, 2.0]]
res = mykmeanssp.fit(init, data, 2, 300, 0.0)
total += 1
ok = (approx_equal(res[0][0], 0.0) and approx_equal(res[1][0], 2.0))
print("A2 already converged :", "PASS" if ok else "FAIL",
      "  got", [["%.4f" % x for x in r] for r in res])
passed += ok

# A3: 3-D, k=3 -> shape check
data = [[1.,1.,1.], [1.,1.,2.], [8.,8.,8.], [8.,9.,8.], [-5.,-5.,-5.], [-5.,-5.,-6.]]
init = [[1.,1.,1.], [8.,8.,8.], [-5.,-5.,-5.]]
res = mykmeanssp.fit(init, data, 3, 300, 0.0)
total += 1
ok = (len(res) == 3 and all(len(r) == 3 for r in res))
print("A3 shape (k=3, d=3)  :", "PASS" if ok else "FAIL",
      "  ->", len(res), "centroids of dim", len(res[0]))
passed += ok


# =====================================================================
# PART B: real datasets (does fit() SURVIVE real scale + shape?)
# init = first k points (a placeholder, NOT kmeans++), so results
# will NOT match output_*.txt -- we only check it runs and stays sane.
# =====================================================================
print("\n=== PART B: smoke tests on the real datasets ===\n")

for fname, k, it in [("input_1.txt", 3, 333),
                     ("input_2.txt", 7, 300),
                     ("input_3.txt", 15, 350)]:
    pts = load_points(fname)
    d = len(pts[0])
    init = [pts[i][:] for i in range(k)]       # first k points as centroids
    res = mykmeanssp.fit(init, pts, k, it, 0.0)

    total += 1
    right_shape = (len(res) == k and all(len(r) == d for r in res))
    all_finite = all(x == x and abs(x) < 1e9 for r in res for x in r)   # x==x catches NaN
    ok = right_shape and all_finite
    print("B %-13s n=%-3d d=%d k=%-2d : %s  (%d centroids, dim %d, finite=%s)"
          % (fname, len(pts), d, k, "PASS" if ok else "FAIL",
             len(res), len(res[0]), all_finite))
    passed += ok


print("\n" + "=" * 50)
print("%d / %d checks passed" % (passed, total))
print("\nNote: PART B does not match output_*.txt on purpose -- that needs")
print("kmeans++ init in kmeans_pp.py. This file only verifies the C fit().")
