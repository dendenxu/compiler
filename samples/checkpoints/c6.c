/**
 * checkpoint 6
 * feature:
 *      integer type
 *      multiple functions & function call
 *      if-else statements
 *      loop statements
 * expected output: 20
 */
int sum_up_to(int a) {
    int sum = 0;
    for (int i=0;i<a;i=i+1)
        sum = sum + i;
    return sum;
}
int main() {
    int a = 5;
    if (a % 2) return 2*sum_up_to(a);
    else return sum_up_to(a);
}