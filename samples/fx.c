int set(int arr[10][10]) {
    arr[3][9] = 27;
    return 0;
}

int main()
{
    int b[10][10];
    set(b);
    return b[3][9];
}