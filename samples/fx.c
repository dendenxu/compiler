int main()
{
    int b[10][10];
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; ++j) {
            b[i][j] = i * j;
        }
    }
    return b[3][9];
}