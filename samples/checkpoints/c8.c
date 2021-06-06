/**
 * checkpoint 8
 * feature:
 *      integer type
 *      multiple functions & function call
 *      nested if-else statements
 *      recursion functions
 *      nested loop statements
 *      break & continue
 * expected output: 595
 */
int fib(int n) {
    // 1 1 2 3 5 8 13 21 34
    if (n <= 0) return 0;
    else if (n == 1) return 1;
    else if (n == 2) return 1;
    else return fib(n - 1) + fib(n - 2);
}
int main() {
    int sum = 0;
    for (int a = 4; a < 10; a++) {
        if (a == 6) continue;
        else if (fib(a) % 2 == 0) {
            for (int b = fib(a); b > 0; b=b-1)
                sum = sum + b;
            break;
        }
    }
    return sum;
}