/* Multi-line Comment */
/**
 * @file    ParserTest.c
 * @note    This file gives test cases to all language elements
 *          (statements, expressions, etc.) in our parser. Each test 
 *          case is marked by a one-line comment.
 */


/* Program */


/* Global Declarations */
int a = 0;
long l = 9999999;
double pi = 3.141592;
float f = 0.03;
// declaration list
char ch = 'a', b = '1', e;
// pointer
char * str;
// array
char thisIsAnArray[19][20][21];


// Function 1
int main() {
    double pi2 = pi * 2;
    double da[10];
    int i, j, t, controller = 1, condition = 0;


    /**
     *  @note   Statements, Control Flows, Scopes
     **/

    /* For Loop */
    for ( int i = 0 ; i < 10 ; i++ )
        /* Block of single statementm && Array Substitution */
        da[i] = i * pi;

    /* Empty Loops */
    while (1);
    do { ; } while (0);
    for ( ; ; ) { ; }

    /* Nested Loop */
    while ( 1 ) 
        for ( int n = 100; n >= 0; n-- )
            while ( controller ) 
                do str = "inside while loop"; 
                while ( condition == "OK" );


    for ( j = 0; j < 10; j++ ) {
        /* If-else Statement */
        if ( da[j] < 10 )
            // continue control
            continue;
        else {
            /* Function Call */
            PrintHello();
            // break control
            break;
        }
    }

    /* Dangling If */
    if ( 1 ) 
        if ( 2 ) l = 222;
        else l = 223;
    else if ( 3 ) l = 333;
    else l = 444;

    /* Nested Scopes */
    {   double t = 6.06;
        {   char t = '0';
            {   int t = 0;
                t = pi * f;
            }
        }
    }

    /* Empty Statements */
    ;;;;;;

    
    /**
     *  @note   Expressions
     **/

    /* Operators & Nested */
    // assignment
    t = 1;
    t = a = -j;
    // t <<= a;
    // t &= 0;
    // t ^= b;
    // t += ch;
    // t *= 20;
    // t %= j;
    // conditional (ternary op)
    1 ? 2 : 3;
    t ? 1 ? 2 : 3 : 4;
    0 ? 2 : 3 ? t ? 4 : 5 : 6;
    // logical
    1 && 2 || 3 && 4;
    1 || (t || 3) && 4; 
    // bitwise
    e ^ e;
    t & e | 3 ^ 5 | (j | e);
    // comparison
    t == 1;
    e >= 'a';
    1 == 2 < 3 != 4 <= 5 > 6 >= 7;
    // shift
    a >> 10;
    2 >> 3 << 4;
    // arithmetic
    i + 1;
    100 + 30 / 4.0;
    // unary
    ~a;
    -100;
    (int)!( *(&t + +1 + -1) + *++str );     // p++ is treated the same as ++p
    
    /* Operator Precedence */
    1 || 0 && 4 == 3 >= 2 - 1 * -1;
    e = i < t ? ++a : a && t;               // e = ( ((a < t) ? (a++) : a) = t )
    // a ? t : e = ch;                      // ERROR, assignment must have a unary lvalue.
    ++da[2];                                // (da[2])++

    
    return 0;
}


/* Function 2, void Return Value, void Parameter */
void PrintHello(void) {
    /* Function Call */
    printf("Hello, Nano C!");
    /* Empty Return */
    return;
}


/* Function 3, Typed Return Value */
int max(int a, int b) {
    // return exp
    return a > b ? a : b;
}