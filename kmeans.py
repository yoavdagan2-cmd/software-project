#1: Check the iter input:
#1a: Parse: iter = argv[2] if given, else 400
#1b Check 1 < iter < 800
#1c: Check iter is a natural number
#1d:  return error if needed- sys.exit(1) + print message


#2: Read the data with sys + use split
#2a: When you read from stdin and split into lines, filter out the empty one before parsing floats, or you'll crash on float(''):
#N - number of points, d- dimension

#3: Check the k input:
#3a: Parse:
#3b: Check 1 < k < N
#3c: Check k is a naturakl number
#3d:  return error if needed- sys.exit(1) + print message


#4: Set global variable: 
#4a: EPSILON = 0.001
#4b: Initialize centroids as first k datapoints- ust LIST and COPY:


#4: Helper functions: 
#a: Update centroids function
##for each point: find it's nearest centriod -> add coordinates to sums[k] -> increment counts[k] -> new centroid = sums[k][j]/ counts[k]

#5: For Loop:
""" for i in range(iter):
    zero sums (Kxd list)
    counts (K list)
    for each point: distance func, sums and counts, 
    old = deep-ish copy of centroids          <- [c[:] for c in centroids]
    update centroids: centroids[k][j] = sums[k][j] / counts[k]
    if all deltas < epsilon: //(Δμ < ε for every centroid- deltas = distance between the updated centriod and the one before this run. STOP: only if ALL )
        break
"""

#6: output: Print centriods (4 digits after dot)

#7: C returns 0/1 