/**
 * checkpoint 4
 * feature:
 *      single function
 *      initilizers & declaration list
 *      assignment expressions
 *      more complicated expression
 *      implicit type casting from int1 to int32
 * expected output: 3
 */
int main() {
    int a = 0, b = 1, c = 2, d = 3;
    a = ((b*c*d) && (a*d)) + (((c+b)/d) || a) + b*c;
    return a;
}