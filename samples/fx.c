int sign(int n) {
    if (n<0) return -1;
    else if (n == 0) return 0;
    else return 1;
}

int main()
{
    return sign(1.0);
}