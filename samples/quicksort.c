int n = 10;
int a[10];

int qsort(int l, int r)
{
    int i = l;
    int j = r;
    int p = a[(l + r) / 2];
    int flag = 1;
    while (i <= j) {
        while (a[i] < p) i = i + 1;
        while (a[j] > p) j = j - 1;
        if (i > j) break;
        int u = a[i];
        a[i] = a[j];
        a[j] = u;
        i = i + 1;
        j = j - 1;
    }
    if (i < r) qsort(i, r);
    if (j > l) qsort(l, j);
    return 0;
}

int rand(int *state)
{
    *state = *state * 5000087 + 198250529;
    return *state % 1000;
}

int initArr(int n)
{
    int state = 474230941;
    int i = 0;
    while (i < n) {
        a[i] = rand(&state);
        i = i + 1;
    }
}

int isSorted(int n)
{
    int i = 0;
    while (i < n - 1) {
        if ((a[i]) > a[i + 1])
            return 0;
        i = i + 1;
    }
    return 1;
}

int main()
{
    // initArr(n);
    for (int i = 0; i < n; i = i + 1) {
        a[i] = n - i - 1;
    }
    // int sorted_before = isSorted(n);
    qsort(0, n - 1);
    // int sorted_after = isSorted(n);
    // if (!(sorted_before == 0 && sorted_after == 1))
    // return 1;
    return a[3];
}