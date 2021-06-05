/**
 * checkpoint 7
 * feature:
 *      integer type
 *      multiple functions & function call
 *      nested if-else statements
 *      recursion functions
 * expected output: 8
 */
int fib(int n) {
    if (n <= 0) return 0;
    else if (n == 1) return 1;
    else if (n == 2) return 1;
    else return fib(n - 1) + fib(n - 2);
}
int main() {
    int a = 6;
    return fib(a);
}