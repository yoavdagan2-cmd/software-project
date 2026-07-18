# Test files
# 1. k=3, max_iter = 600
# 2. k=7, max_iter = not provided
# 3. k=15, max_iter = 300%
EXECUTABLE=$1
echo "Running tests for $EXECUTABLE"
echo test1
$EXECUTABLE 3.0 0600 < test/input_1.txt > out1.txt
echo $?
echo compare out1
diff out1.txt test/output_1.txt
echo $?
echo test2
$EXECUTABLE 7 < test/input_2.txt > out2.txt
echo $?
echo compare out2
diff out2.txt test/output_2.txt
echo $?
echo test3
$EXECUTABLE 15 300 < test/input_3.txt > out3.txt
echo $?
echo compare out3
diff out3.txt test/output_3.txt
echo $?
echo Parameters validation
echo test1: No arguments provided. Should print: An Error Has Occurred
$EXECUTABLE
echo $?
echo test2: Algorithm does not converge
$EXECUTABLE 3 5 < test/input_1.txt > tmp.txt
echo $?
echo compare out
diff tmp.txt test/output_1.txt
echo $?
echo test3: Success return value
echo test4: Failure return value
echo test5: Invalid K parameter
$EXECUTABLE 1 < test/input_1.txt
echo $?
$EXECUTABLE 800 < test/input_1.txt
echo $?
$EXECUTABLE 3.5 < test/input_1.txt
echo $?
echo test6: Invalid iters parameter
$EXECUTABLE 3 1 < test/input_1.txt
echo $?
$EXECUTABLE 3 800 < test/input_1.txt
echo $?
$EXECUTABLE 3 8.1 < test/input_1.txt
echo $?
echo test7: Empty file
$EXECUTABLE 3 < test/input_empty.txt
echo $?
echo test8: Valgrind
valgrind -s ./build/kmeans 3 600 < test/input_1.txt
echo $?
echo test9: Too many arguments provided. Should print: An Error Has Occurred
$EXECUTABLE 3 600 1 < test/input_1.txt
echo $?
