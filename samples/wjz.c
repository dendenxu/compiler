#include <stdio.h>

int main() {
    // int a = 1, b = 3, sum;
    int a[3][3] = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };
    int ** aptr = (int**)a;
    // sum = 0;
    // sum = a + b;
    printf("%d\n", a[0][0]);
    printf("%d\n", a[1][1]);
    printf("%d\n", *aptr);    // *(aptr + 1)
    printf("%p, %p\n", &a[0], aptr + 1);

    return 0;
}