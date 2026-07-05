import sys
from math import dist, sqrt

def sq_distance(p, q):
    total = 0
    for i in range(len(p)):
        cur_dif = p[i]-q[i]
        total += pow(cur_dif,2)
    return total

    
#4: Helper functions: 
#a: Update centroids function
##for each point: find it's nearest centriod -> add coordinates to sums[k] -> increment counts[k] -> new centroid = sums[k][j]/ counts[k]

def update_centroids(data, centriods, k ,d):
    #Initialize zero accumulators
    sums = [[0.0] * d for _ in range (k)]
    counts = [0]* k

    #Assign each point to the nearest centroid
    for point in data:
        closest_cent = min(range(k), key = lambda j:sq_distance(point, centriods[j]))
        for j in range(d):
            sums[closest_cent][j] += point[j]
        counts[closest_cent] += 1

    #Format new centroids
    new_centroids = [[sums[c][j] / counts [c] for j in range(d)]
                        for c in range(k)]
    
    return new_centroids

def parse_input(input, error_msg):
    if not input.isdigit():
        sys.exit(error_msg)
    return int(input)

EPSILON = 0.001
ITER_ERROR = "Incorrect maximum iteration!"
K_ERROR = "Incorrect number of clusters!"
GEN_ERROR = "An Error Has Occured"

k = 0
data = []


#1: Check the iter input:
#1a: Parse: iter = argv[2] if given, else 400
#1b Check 1 < iter < 800
#1c: Check iter is a natural number
#1d:  return error if needed- sys.exit(1) + print message

try:
    iter = parse_input(sys.argv[2], ITER_ERROR)
    sys.exit(1)
except:
    iter = int(400)

if not 1 < iter < 800:
    print(ITER_ERROR)
    sys.exit(1)

#2: Read the data with sys + use split
#2a: When you read from stdin and split into lines, filter out the empty one before parsing floats, or you'll crash on float(''):
#N - number of points, d- dimension

for line in sys.stdin.read().split("\n"):
    if line.strip() == '': #skip the empty trailing line
        continue
    data.append([float(x) for x in line.split(',')])

N = len (data)
d = len(data[0])
print("Number of points", N)
#3: Check the k input:
#3a: Parse:
#3b: Check 1 < k < N
#3c: Check k is a natural number
#3d:  return error if needed- sys.exit(1) + print message
k = parse_input(sys.argv[1], K_ERROR)
if not 1 < k < N:
    print(K_ERROR)
    sys.exit(1)

#4: Initialize centroids as first k datapoints- use LIST and COPY:
cent_lst = [point[:] for point in data[:k]]

#5: For Loop:
for i in range(iter):
    new_centroids = update_centroids(data, cent_lst, k, d)
    convereged = all(dist((new_centroids[k_i]), cent_lst[k_i]) < EPSILON
                     for k_i in range(k))
    cent_lst = new_centroids
    if convereged:
        break

#6: output: Print centriods (4 digits after dot)
print(cent_lst)