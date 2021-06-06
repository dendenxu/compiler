/**
 * checkpoint 12
 * feature:
 *      integer type & float type & void type
 *      pointer type & array type
 *      & and * operator
 *      type casting:
 *          xd array -> pointer
 *          int <-> float
 *      calculations:
 *          *(pointer + integer)
 *      quicksort
 *      random integer generation
 * expected output: 1
 */

int qsort(int * a, int l, int r)
{
    int i = l;
    int j = r;
    int p = *(a + ((l + r)/2));
    int flag = 1;
    while (i <= j) {
        while (*(a+i) < p) i = i + 1;
        while (*(a+j) > p) j = j - 1;
        if (i > j) break;
        int u = *(a+i);
        *(a+i) = *(a+j);
        *(a+j) = u;
        i = i + 1;
        j = j - 1;
    }
    if (i < r) qsort(a, i, r);
    if (j > l) qsort(a, l, j);
    return 0;
}

// random floating point number distributed uniformly in [0,1]
float rand(float *r) {
    float base=256.0;
    float a=17.0;
    float b=139.0;
    float temp1=a*(*r)+b;
    float temp2=(float)(int)(temp1/base);
    float temp3=temp1-temp2*base;
    *r=temp3;
    float p=*r/base;
    return p;
}

int initArr(int* a, int n)
{
    float state = 114514.0;
    int i =0;
    while (i < n) {
        *(a + i) = (int)(255*rand(&state));
        i = i + 1;
    }
}

int isSorted(int *a, int n)
{
    int i = 0;
    while (i < n - 1) {
        if ( (*(a+i)) > (*(a+i+1)))
            return 0;
        i = i + 1;
    }
    return 1;
}

int main()
{
    int n = 100;
    int arr[100];
    int * a = (int*)arr;
    initArr(a, n);
    qsort(a, 0, n - 1);
    return isSorted(a, n);
}