import sys
from math import dist

EPSILON = 0.001
ITER_ERROR = "Incorrect maximum iteration!"
K_ERROR = "Incorrect number of clusters!"
GEN_ERROR = "An Error Has Occurred"
    
def parse_input(input, error_msg):
    '''
    Parse input data as a natual number
    Accepts integer-valued input including float notation (e.g. "3", "3.0",
    "03"). Rejects non-integers ("3.5") and non-numbers ("abc").

    Args:
        input: the raw command-line string
        error_msg: string message to print upon fail
    
    Return:
        Value as an int
            
    '''
    try: 
        num = float(input)
    except ValueError:
        print(error_msg)
        sys.exit(1)
    if num != int(num):
        print(error_msg)
        sys.exit(1)
    return int(num)


def read_data():
    '''Read input data points from standard input
    Assuming each line is one point comma-seperated floats. Including one blank line trailing are skipped

    Return:
        A tuple (N, d, data)
            N: number of points
            d: dimenssion
            data: list of points, each a list of d floats
    '''
    data = []
    for line in sys.stdin.read().split("\n"):
        if line.strip() == '': #skip the empty trailing line
            continue
        data.append([float(x) for x in line.split(',')])

    N = len (data)
    d = len(data[0])
    
    return N ,d, data

def read_params(data, N ,d):
    '''Read input parameters (iter, k)
        K must satisfy 1 < K < n. iter (optional; default 400) must satisfy
        1 < iter < 800. Both must be natural numbers.
    
    Args: 
        data: input data
        N: amount of points
        d: dimension of each point

    Returns:
        A tuple (k, iter) of validated ints
            k: k input
            iter: number of iterations

     Exits:
        Prints the relevant message and exits 1 on invalid K or iter.

    '''
    if len(sys.argv) == 3:
        iter = parse_input(sys.argv[2], ITER_ERROR)
        if not 1 < iter < 800:
            print(ITER_ERROR)
            sys.exit(1)
    else:
        iter = 400

    #3: Check the k input:
    #3a: Parse:
    #3b: Check 1 < k < N
    #3c: Check k is a natural number
    #3d:  return error if needed- sys.exit(1) + print message
    k = parse_input(sys.argv[1], K_ERROR)
    if not 1 < k < N:
        print(K_ERROR)
        sys.exit(1)
    
    return k, iter

def sq_distance(p, q):
    '''
    squared Euclidean distance between two points
    Squared (no square root) because it is used only to compare distances
    when finding the nearest centroid, where the ordering is unchanged.

    Args:
        p (list of floats): first point 
        q (list of floats): secound poinr
    
    Returns:
        total(float): square distance between the points
    '''
    total = 0
    for i in range(len(p)):
        cur_dif = p[i]-q[i]
        total += pow(cur_dif,2)
    return total

def update_centroids(data, centriods, k ,d):
    '''
    Re-calulate distance between centroid and current cluster and update the centroids according to the cluster.

    Args:
        data(list): input data (points)
        centroid(list): current centroids
        k: k parameter
        d: dimenssion
    
    Return:
        new_centroids(list): updated list of centroids
    '''
    #Initialize zero accumulators
    sums = [[0.0] * d for _ in range (k)]
    counts = [0] * k

    #Assign each point to the nearest centroid
    for point in data:
        closest_cent = min(range(k), key = lambda j:sq_distance(point, centriods[j]))
        for j in range(d):
            sums[closest_cent][j] += point[j]
        counts[closest_cent] += 1

    #Format new centroids
    new_centroids = []
    for c in range(k):
        if counts[c] == 0:
            new_centroids.append(centriods[c][:])
        else:
            new_centroids.append([sums[c][j] / counts[c] for j in range(d)])
    
    return new_centroids

def k_means(data, k, d, iter):
    '''
    Re-cluster and update centroids until convergance

    Args:
        data: points list
        k: initial amount of points to use
        d: point dimension
        iter: ammount of itterations
    
    Return:
        cent_lst: list of centroids

    '''
    #4: Initialize centroids as first k datapoints- use LIST and COPY:
    cent_lst = [point[:] for point in data[:k]]

    #5: For Loop:
    for i in range(iter):
        new_centroids = update_centroids(data, cent_lst, k, d)
        converged = all(dist((new_centroids[k_i]), cent_lst[k_i]) < EPSILON
                        for k_i in range(k))
        cent_lst = new_centroids
        if converged:
            break
    
    return cent_lst

def print_cent(centroids, i=4):
    '''
    Prints final centroids list with i decimal

    Args:
        centroisd(list): centroids list to pring
        i (int): decimal plcaes
    
    Return: 
        null
    '''
    for cent in centroids:
        print(",".join(f'{coord:.{i}f}' for coord in cent))

def main():
    if not len(sys.argv) in (2,3):
        print(GEN_ERROR)
        sys.exit(1)
    

    N ,d, data = read_data()
    k, iter = read_params(data, N ,d)
    centroids = k_means(data, k ,d, iter)
    print_cent(centroids)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise

    except Exception:
        print(GEN_ERROR)
        sys.exit(1)