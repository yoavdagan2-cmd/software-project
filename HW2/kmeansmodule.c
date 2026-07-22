/*Python
Python side (kmeans_pp.py):
    data is a numpy array
    → data.tolist()  turns it into a Python list of lists
    → mykmeanssp.fit(centroids.tolist(), data.tolist(), k, iter, eps)
    Part1: Read command arguments + validate the input
    Part2: Combine and pre-process data
    Part3: Call the kmeans++ (Algorithm 1 ine HW2 page). Output: Initial centroids to use
    Part4: Import c module mykmeanssp + call fit() function with initial centriods, datapoints etc
    Part5: Print the fit function output

*/

/*C:
C side (fit() in kmeansmodule.c):
    receives the Python list of lists (a PyObject*)
    → pylist_to_c() mallocs a C array and copies the numbers in   ← this is the conversion
    → run_kmeans() computes on that C array
    → c_to_pylist() builds a Python list of lists from the C result
    → returns that list

Python side:
    gets a list of lists back
    → (optional) np.array(result)  if you want it as numpy again
*/


#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

double squared_distance(double *p1, double *p2, int d);
int closest_centroid(double *point, double **centroids, int k, int d);
int update_centroids(double **points, double **centroids, int k, int d, int n, double eps);


static double** run_kmeans(double **points, double **centroids, int n, int d, int k , int iter, double eps)
{

    int iter_i, conv;

    /* run k-means iterations */
    for (iter_i = 0; iter_i < iter; iter_i++) {
        conv = update_centroids(points, centroids, k, d, n, eps);
        if (conv == -1) {
            return NULL;
        }
        if (conv) break;
    }

    return centroids; 

    
    }
int update_centroids(double **points, double **centroids, int k, int d, int n, double eps)
{
    double **sums;
    int *counts;
    int i;
    int j;
    int closest_cent;
    double new_value;
    double diff;
    double squared_shift;
    int converged = 1;
    

    sums = malloc(k * sizeof(double *));
    counts = malloc(k * sizeof(int));

    if (sums == NULL || counts == NULL) {
        free(sums);
        free(counts);
        printf("An Error Has Occurred\n");
        return -1;
    }

    for (i = 0; i < k; i++) {
        sums[i] = malloc(d * sizeof(double));

        if (sums[i] == NULL) {
            int t;
            for (t = 0; t < i; t++) {
                free(sums[t]);
            }
            free(sums);
            free(counts);
            printf("An Error Has Occurred\n");
            return -1;
        }

        counts[i] = 0;

        for (j = 0; j < d; j++) {
            sums[i][j] = 0.0;
        }
    }

    for (i = 0; i < n; i++) {
        closest_cent = closest_centroid(points[i], centroids, k, d);
        counts[closest_cent]++;

        for (j = 0; j < d; j++) {
            sums[closest_cent][j] += points[i][j];
        }
    }

    for (i = 0; i < k; i++) {
        if (counts[i] == 0) {
            continue;
        }

        squared_shift = 0.0;
        for (j = 0; j < d; j++) {
            new_value = sums[i][j] / counts[i];
            diff = new_value - centroids[i][j];
            centroids[i][j] = new_value;
            squared_shift += diff * diff;
        }
        if (squared_shift >= eps * eps) {
            converged = 0;
        }
    }

    for (i = 0; i < k; i++) {
        free(sums[i]);
    }

    free(sums);
    free(counts);

    return converged;
}


double squared_distance(double *p1, double *p2, int d)
{
    int j;
    double diff;
    double sum;

    sum = 0.0;

    for (j = 0; j < d; j++) {
        diff = p1[j] - p2[j];
        sum += diff * diff;
    }

    return sum;
}

int closest_centroid(double *point, double **centroids, int k, int d)
{
    int i;
    int min_dist_idx;
    double curr_dist;
    double min_dist;

    min_dist_idx = 0;
    min_dist = squared_distance(point, centroids[0], d);

    for (i = 1; i < k; i++) {
        curr_dist = squared_distance(point, centroids[i], d);

        if (curr_dist < min_dist) {
            min_dist = curr_dist;
            min_dist_idx = i;
        }
    }

    return min_dist_idx;
}


/*Python list of lists -> malloc'd C matrix (rows x cols)*/
static double** pylist_to_c(PyObject *lst, int rows, int cols)
{
    int i,j;
    double **m = malloc(rows * sizeof(double *));
    if(m == NULL) return NULL;
    for (i=0 ; i < rows ; i++){
        PyObject *row = PyList_GetItem(lst, i);
        m[i] = malloc(cols * sizeof(double));
        if (m[i] == NULL) return NULL;
        for (j=0; j<cols; j++){
            PyObject *item = PyList_GetItem(row, j);
            m[i][j] = PyFloat_AsDouble(item);
        }
    }
    return m;
}

/*C matrix (rows x cols) -> Python list of lists*/
static PyObject* c_to_pylist(double **m, int rows, int cols){
    int i,j;
    PyObject *out = PyList_New(rows);
    for(i=0; i< rows; i++){
        PyObject *row = PyList_New(cols);
        for(j=0; j<cols; j++){
            PyList_SetItem(row, j, PyFloat_FromDouble(m[i][j]));
        }
        PyList_SetItem(out, i , row);
    }
    return out;
}


/*free a rows x_ matrix allocated by pylist_to_c*/
static void free_matrix(double **m, int rows){
    int i;
    if(m == NULL) return;
    for(i=0; i < rows; i++) free(m[i]);
    free(m);
}

//Function/ module fit()


static PyObject* fit(PyObject *self, PyObject *args){
    PyObject *py_centroids, *py_data, *py_result;
    int k, max_iter, n, d;
    double eps;
    double **centroids, **data, **result;

    /*Parse the python variables into C arguments*/
    if(!PyArg_ParseTuple(args, "OOiid", &py_centroids, &py_data, &k, &max_iter, &eps)){
        return NULL; /* wrong arguments -> Python raises TypeError */
    }

    n = (int)PyList_Size(py_data);
    d = (int)PyList_Size(PyList_GetItem(py_data, 0));

    data = pylist_to_c(py_data, n, d);
    centroids = pylist_to_c(py_centroids, k, d);

    if (data == NULL || centroids == NULL) return PyErr_NoMemory();


    /*Run the kmeans module*/
    result = run_kmeans(data, centroids, n, d, k, max_iter, eps);
    if (result == NULL){
        free_matrix(data, n);
        free_matrix(centroids, k);
        return PyErr_NoMemory();
    }

    /*Return the C centroids in a python list*/
    py_result = c_to_pylist(result, k ,d);

    /*Cleanup C memory*/
    free_matrix(data, n);
    free_matrix(centroids, k);


    return py_result;
}


static PyMethodDef kmeans_methods[] = {
    {"fit", 
    (PyCFunction)fit, 
    METH_VARARGS,
    PyDoc_STR("Run k-means given initial centroids: return final centroids.")},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef kmeans_module = {
    PyModuleDef_HEAD_INIT,
    "mykmeanssp",
    NULL,
    -1,
    kmeans_methods
};

PyMODINIT_FUNC PyInit_mykmeanssp(void) {   
    return PyModule_Create(&kmeans_module);
}



