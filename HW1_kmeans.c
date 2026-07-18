#include <stdio.h>
#include <stdlib.h>
#define DEFAULT_ITER 400
#define MAX_ITER 800
#define EPSILON 0.001

double squared_distance(double *p1, double *p2, int d);
int closest_centroid(double *point, double **centroids, int k, int d);
void print_centroids(double **points, int k, int d);
void print_points(double **points, int n, int d);
int parse_positive_int(char *str, int *result);
int update_centroids(double **points, double **centroids, int k, int d, int n);

int main(int argc, char *argv[])
{
    int k;
    int iter;
    double *all_points_arr;
    double **points;
    double *temp;
    double x;
    char c;
    int result;
    int size;
    int n;
    int capacity;
    int curr_dim;
    int first_line;
    int d;
    int i;
    int j;
    if (argc != 2 && argc != 3) {
        printf("An Error Has Occurred\n");
        return 1;
    }



/* parse k */
if (!parse_positive_int(argv[1], &k)) {
    printf("Incorrect number of clusters!\n");
    return 1;
}

/* parse iter */
if (argc == 3) {
    if (!parse_positive_int(argv[2], &iter)) {
        printf("Incorrect maximum iteration!\n");
        return 1;
    }
} else {
    iter = DEFAULT_ITER;
}

/* check iter */
if (iter <= 1 || iter >= MAX_ITER) {
    printf("Incorrect maximum iteration!\n");
    return 1;
}







    /* parse input points into an array */
    size = 0;
    n = 0;
    capacity = 10;
    curr_dim = 0;
    first_line = 1;
    d = 0;
    all_points_arr = malloc(capacity * sizeof(double));

    if (all_points_arr == NULL) {
        printf("An Error Has Occurred\n");
        return 1;
    }

    result = scanf("%lf%c", &x, &c);
    while (result == 2 || result == 1) {
        if (result == 1) {
            c = '\n';
        }

        if (size == capacity) {
            capacity = capacity * 2;
            temp = realloc(all_points_arr, capacity * sizeof(double));

            if (temp == NULL) {
                free(all_points_arr);
                printf("An Error Has Occurred\n");
                return 1;
            }
            all_points_arr = temp;
        }

        all_points_arr[size] = x;
        size++;
        curr_dim++;

        if (c != ',' && c != '\n') {
            free(all_points_arr);
            printf("An Error Has Occurred\n");
            return 1;
        }

        if (c == '\n') {
            if (first_line) {
                first_line = 0;
                d = curr_dim;
            } else if (curr_dim != d) {
                free(all_points_arr);
                printf("An Error Has Occurred\n");
                return 1;
            }
            n++;
            curr_dim = 0;
        }

        if (result == 1) {
            break;
        }

        result = scanf("%lf%c", &x, &c);
    }
    if (result == 0 || curr_dim != 0 || first_line) {
        free(all_points_arr);
        printf("An Error Has Occurred\n");
        return 1;
    }

if (k <= 1 || k >= n) {
    free(all_points_arr);
    printf("Incorrect number of clusters!\n");
    return 1;
}

    /* convert the flat array into an array of rows */
    points = malloc(n * sizeof(double *));

    if (points == NULL) {
        free(all_points_arr);
        printf("An Error Has Occurred\n");
        return 1;
    }

    for (i = 0; i < n; i++) {
        points[i] = malloc(d * sizeof(double));

        if (points[i] == NULL) {
            int t;
            for (t = 0; t < i; t++) {
                free(points[t]);
            }
            free(points);
            free(all_points_arr);
            printf("An Error Has Occurred\n");
            return 1;
        }

        for (j = 0; j < d; j++) {
            points[i][j] = all_points_arr[i * d + j];
        }
    }

  

    free(all_points_arr);

    /* initiate centroids as first k points */
    {
        double **centroids;
        int iter_i;

        centroids = malloc(k * sizeof(double *));

        if (centroids == NULL) {
            /* cleanup */
            for (i = 0; i < n; i++) {
                free(points[i]);
            }
            free(points);
            printf("An Error Has Occurred\n");
            return 1;
        }

        for (i = 0; i < k; i++) {
            centroids[i] = malloc(d * sizeof(double));
            if (centroids[i] == NULL) {
                int t;
                for (t = 0; t < i; t++) free(centroids[t]);
                free(centroids);
                for (t = 0; t < n; t++) free(points[t]);
                free(points);
                printf("An Error Has Occurred\n");
                return 1;
            }
            /* copy first k points as initial centroids */
            for (j = 0; j < d; j++) {
                centroids[i][j] = points[i][j];
            }
        }

        /* run k-means iterations */
        for (iter_i = 0; iter_i < iter; iter_i++) {
            int conv;
            conv = update_centroids(points, centroids, k, d, n);
            if (conv == -1) {
                for (i = 0; i < n; i++) free(points[i]);
                free(points);
                for (i = 0; i < k; i++) free(centroids[i]);
                free(centroids);
                return 1;
            }
            if (conv) break;
        }

        /* print final centroids */
        print_centroids(centroids, k, d);

        /* cleanup */
        for (i = 0; i < n; i++) free(points[i]);
        free(points);
        for (i = 0; i < k; i++) free(centroids[i]);
        free(centroids);
    }

    return 0;
}

int update_centroids(double **points, double **centroids, int k, int d, int n)
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
        if (squared_shift >= EPSILON * EPSILON) {
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

void print_centroids(double **points, int k, int d)
{
    int i;
    int j;

    for (i = 0; i < k; i++) {
        for (j = 0; j < d; j++) {
            printf("%.4f", points[i][j]);

            if (j < d - 1) {
                printf(",");
            }
        }

        printf("\n");
    }
}

void print_points(double **points, int n, int d)
{
    int i;
    int j;

    for (i = 0; i < n; i++) {
        for (j = 0; j < d; j++) {
            printf("%.4f", points[i][j]);

            if (j < d - 1) {
                printf(",");
            }
        }

        printf("\n");
    }
}

int parse_positive_int(char *str, int *result)
{

    int i;
    int value;
    int seen_dot;

    if (str[0] == '\0') {
        return 0;
    }
    value = 0;
    seen_dot = 0;

    for (i = 0; str[i] != '\0'; i++) {

        if (str[i] == '.') {
            if (seen_dot || i == 0) {
                return 0;
            }
            seen_dot = 1;
            continue;
        }

        if (str[i] < '0' || str[i] > '9') {
            return 0;
        }
        if (seen_dot) {
            if (str[i] != '0') {
                return 0;
            }
        } else {
            value = value * 10 + (str[i] - '0');
        }
    }
    *result = value;
    return 1;
}
