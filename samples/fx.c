int sum_up_to(int bound) {
    int sum = 0;
    for (int i=0;i<bound;i=i+1) {
        sum = sum+i;
    }
    return sum;
}

int main() {
    int a=2;
    int b=10;
    a = a*sum_up_to(b);
    return a;
}