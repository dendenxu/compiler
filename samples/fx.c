int a[10];
int main() {
    for (int i=0;i<10;i++) {
        a[i] = i;
    }
    int * b = (int*)a;
    return *(b+4);
}