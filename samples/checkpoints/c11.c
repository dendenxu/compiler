/**
 * checkpoint 11
 * feature:
 *      integer type & float type & void type
 *      pointer type & array type
 *      & and * operator
 *      type casting:
 *          xd array -> pointer
 *          int <-> float
 *      gloabl variables
 *      multi-scopes
 *      calculations:
 *          *(pointer + integer)
 * expected output: 12
 */

int n = 10;
int a[10][10];

int main() {
    int i = 3, j = 3;
    for (int i=0; i<n;i=i+1) {
        for (int j=0; j<n; j=j+1) {
            a[i][j] = i+j;
        }
    }
    int * arr_ptr = (int*)a;
    *(arr_ptr + i*n + j) = 2 * *(arr_ptr + i*n + j);
    return a[i][j];
}