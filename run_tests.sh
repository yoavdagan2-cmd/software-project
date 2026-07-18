#!/bin/bash
# Runs the three course tests from test_readme.txt and diffs against expected output.
# Put this next to kmeans_pp.py, kmeansmodule.c, setup.py and all input_*/output_* files.
#
# Usage:  bash run_tests.sh
#
# NOTE: adjust the argument order in the python3 lines below to match YOUR spec.
#       Current assumption:  kmeans_pp.py  K  ITER  EPS  file1  file2

set -u

echo "== building the C extension =="
python3 setup.py build_ext --inplace || { echo "BUILD FAILED"; exit 1; }
echo

pass=0
total=0

run_one () {
    num="$1"; k="$2"; it="$3"; eps="$4"; f1="$5"; f2="$6"
    total=$((total+1))
    echo "== test $num: k=$k iter=$it eps=$eps =="
    python3 kmeans_pp.py "$k" "$it" "$eps" "$f1" "$f2" > "my_output_$num.txt" 2>err.txt
    if [ $? -ne 0 ]; then
        echo "  RUN ERROR:"; sed 's/^/    /' err.txt; echo; return
    fi
    if diff -q "my_output_$num.txt" "output_$num.txt" >/dev/null; then
        echo "  PASS"
        pass=$((pass+1))
    else
        echo "  FAIL — first differences (< yours, > expected):"
        diff "my_output_$num.txt" "output_$num.txt" | head -8 | sed 's/^/    /'
    fi
    echo
}

run_one 1 3  333 0 input_1_db_1.txt input_1_db_2.txt
run_one 2 7  300 0 input_2_db_1.txt input_2_db_2.txt
run_one 3 15 350 0 input_3_db_1.txt input_3_db_2.txt

echo "========================================"
echo "$pass / $total tests passed"
