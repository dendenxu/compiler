/**
 * checkpoint 10
 * feature:
 *      integer type & pointer type
 *      array type
 *      & and * operator
 *      value swap with pointers
 * expected output: 7
 */
void swap(int* a, int* b) {
    int c = *a;
    *a = *b;
    *b = c;
}
int main() {
    int a[3][3];
    a[0][0] = 0; a[0][1] = 1; a[0][2] = 2;
    a[1][0] = 3; a[1][1] = 4; a[1][2] = 5;
    a[2][0] = 6; a[2][1] = 7; a[2][2] = 8;
    int b=1, c=2;
    int *ptr_to_b = &b;
    int *ptr_to_c = &c;
    swap(ptr_to_b,ptr_to_c);
    return a[b][c];
}