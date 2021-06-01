struct Message {
    unsigned char ip[4];
    char name[20];
    char msg[100];
    int status_code;
    int timestamp;
};

int main()
{
    static const unsigned int a = 0;
    char b = 'a';
    int b, c;
    b = 1;
    c = a + b;

    const char* msg = "Hello, world.";
    const char* name = "compiler";
    struct Message m = {{192, 168, 0, 1}, name, msg, 200, 16384};

    return 0;
}