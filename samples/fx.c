int sum_up_to(int a) {
    int sum =0;
    for (int i=0;i<a;i=i+1) {
        if (i == 3) continue;
        sum = sum+i;
        if (sum > 10) break;
    }
    return sum;
}

int main() {
    int a = 10;
    return sum_up_to(a);
}