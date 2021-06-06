/**
 * checkpoint 9
 * feature:
 *      void return type
 *      integer type & pointer type
 *      & and * operator
 *      value swap with pointers
 * expected output: 2
 */
void swap(int *a, int *b) {
    int c = *a;
    *a = *b;
    *b = c;
}
int main() {
    int a=1, b=2;
    int *c = &a;
    int *d = &b;
    swap(c,d);
    return a;
}