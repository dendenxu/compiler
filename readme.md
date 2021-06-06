# Nano C Compiler

The C programming language compiler with extremely limited functionality.

We'd only implement a subset of a subset of C. Don't even expect preprocessing.

And **do remember to delete these lines after this repo goes public**

## Lexical Analysis

### Token Specification

- Types: `int`, `long`, `double`, `float`, `char`, `void`, `[]`, **pointer**
- Control Flow: `if`, `else`, `while`, `for`, `continue`, `break`, `do-while`
- Function: `return`, **typed functions**, **scope**(`{}` `;`)
- Operators (with precedence):
  1. `()` `[]` Function Call, Array Subscription
  2. `-` `+` `++` `--` `!` `&` `*` `~` `(type)` Negation, Positive Number, Minus Minus, Plus Plus, Logical Not, Bitwise And, Get Element Of Pointer, Bitwise Not, Type Casting
  3. `*` `/` `%` Times, Divide, Modulus
  4. `+` `-` Plus, Minus
  5. `<<` `>>` Shift Left, Shift Right
  6. `<` `<=` `>` `<=` Less Than, Less Than Or Equal To, Greater Than, Greater Than Or Equal To
  7. `==` `!=` Equality, Inequality
  8. `&` Get Element Pointer
  9. `^` Bitwise XOR
  10. `|` Bitwise Or
  11. `&&` Logical And
  12. `||` Logical Or
  13. `?:` Conditional Expression
  14. `=` `<<=` `>>=` `&=` `|=` `^=` `+=` `-=` `/=` `*=` `%=` Assignment Operation
- Comment:
  1. `//` (one-line comment)
  2. `/* */` (multi-line comment)

### Token Definition

Token List:

```python
keywords = (
    'INT', 'LONG', 'FLOAT', 'DOUBLE', 'CHAR',
    'UNSIGNED', 'CONST', 'VOID', "STATIC"
    'ENUM', 'STRUCT', 'UNION', 'IF', 'ELSE',
    'DO', 'WHILE', 'FOR', 'CONTINUE', 'BREAK', 'RETURN'
)
# All the tokens recognized by the lexer
tokens = keywords + (
    # Identifiers
    'ID',

    # constants
    'INT_CONST_DEC',
    'FLOAT_CONST',
    'CHAR_CONST',

    # String literals
    'STRING_LITERAL',

    # Operators
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
    'LOR', 'LAND', 'LNOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',

    # Assignment
    'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL',
    'PLUSEQUAL', 'MINUSEQUAL',
    'LSHIFTEQUAL', 'RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL',
    'OREQUAL',

    # Increment/decrement
    'PLUSPLUS', 'MINUSMINUS',

    # Structure dereference (->)
    'ARROW',

    # Conditional operator (?)
    'CONDOP',

    # Delimeters
    'LPAREN', 'RPAREN',         # ( )
    'LBRACKET', 'RBRACKET',     # [ ]
    'LBRACE', 'RBRACE',         # { }
    'COMMA', 'PERIOD',          # . ,
    'SEMI', 'COLON',            # ; :
)
```

Important Regular Expression Definitions

```python
identifier = r'[a-zA-Z_$][0-9a-zA-Z_$]*'

decimal_constant = '(0+)|[1-9][0-9]*'

cconst_char = r"""[^'\\\n]"""
char_const = "'"+cconst_char+"'"
multicharacter_constant = "'"+cconst_char+"{2,4}'"
unmatched_quote = "('"+cconst_char+"*\\n)|('"+cconst_char+"*$)"

# string literals (K&R2: A.2.6)
string_char = r"""[^"\\\n]"""
string_literal = '"'+string_char+'*"'

# floating constants (K&R2: A.2.5.3)
exponent_part = r"""([eE][-+]?[0-9]+)"""
fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
floating_constant = '(((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+'))[FfLl]?)'

# empty space
t_ignore = ' \t'

# Comment
t_ignore_SING_COMMENT = r'//.*?\n'
t_ignore_MULT_COMMENT = r'/\*(\*(?!\/)|[^*])*\*\/'
```

We used the `ply` (Python Lex Yacc) to help better recognize regular expressions and BNF grammars to make our life easier.

We only need to import the "lexer" from the ply module using `from ply import lex`

And build it with `lex.build`, passing specific module into the build function.

The lexer utilizes Python's object reflection (introspection) so it needs the current building context to extract regular expressions and map them to corresponding tokens.

It mainly recognize variables defined as `t_TOKEN_NAME`, the content of the variable corresponds to the regular expression, and the `TOKEN_NAME` part would be the token this RE recognizes for.

### Specific Optimizations

#### Token Removal

By using `t_ignore` pattern or not returning the recognized token, we discard unwanted information provided by the program source code for readability of us **humans** (but not for the **parser**)

- White Space
- New Line Characters
- Comments
  - Single-lined comment
  - Multi-lined comment

```python
# empty space
t_ignore = ' \t'
```



#### Line Number Memory

To help the user pinpoint what's gone wrong the tokenization process, we "remembers" every token's location (in terms of line number and token column), which will even be used in the later syntax analysis process.

Specifically, we used `r'\n+'` to indicate newline(s)

- It's important to notice that **multi-line comment/single-line comment might also consume the newline character**
- Also note that `r'\n+'` regular expression might contain multiple newline characters

So we should use patterns like `t.lexer.lineno += t.value.count("\n")` to update the new line count accordingly.

```python
# Define a rule so we can track line numbers
def update_lineno(self, t):
    t.lexer.lineno += t.value.count("\n")

# Comment
def t_SINGLE_LINE_COMMENT(self, t):
    r'//.*?\n'
    self.update_lineno(t)

def t_MULTI_LINE_COMMENT(self, t):
    r'/\*(\*(?!\/)|[^*])*\*\/'
    self.update_lineno(t)

def t_NEWLINE(self, t):
    r'\n+'
    self.update_lineno(t)
```



#### Order of Regular Expression

We carefully optimized the **order** in which each regular expression is provided to the lexer, to make sure some overlapping definitions don't get mixed up, for example:

- `//` for line comment comes before `/` Operator
- `/*` for multi-line comment comes before `/` Operator
- `ID` for identifier comes after other constants that may include characters and numbers (**char literal, string literal, int/float constant values**)



## Syntax Analysis

### Grammar Syntax for Nano C language

Firstly, let's take a comprehensive look at our grammar:

1. We *don't* implement preprocessing like **macros** and **includes**

2. We *don't* implement multi-file compilation, as a direct cause of the first rule

3. Thus we want a program to define the whole program (a single C source file)

4. This program should contain some **global variable definitions**

5. This program should also contain some **function definitions**

6. We *don't* support **external linkage** variable definition due to rule number one

7. We *don't* support function/global variable **declaration** since it won't be of much use in this setup.

8. Every valid statement should be 

    1. A **block of statements**

        Wrapped within two paired curly brackets, namely `{`, `}`

        This block can **recursively contain other statements**

        You can happily and inconsequently do `{{{{{;}}}}}`

    2. Some **control flows**

        1. `for (int i = 0; i < 100 ; i++ ) {;}` for loops

        2. `while (1) {;}` while loops

        3. `do {;} while(1);` do-while loops

        4. `if(1) {;} else if(2) {;} else {;}` if-else statements

        5. Note that we forbid empty block `{}`

        6. But **one single (non-blocked) statement will be valid**, for example: `if(1) print(1); else print(2);`

            Actually, the nested `if` `else if` `else` block is implemented by viewing the second `if-else` block as a single statement

            `if (1) {;} else { if (2) {;} else {;} }`

            You can do crazy things as long as you remember you're writing out one single statement

            `while (1) while(0)while(controller) do p = "inside while loop"; while ( condition == "OK" );`

        7. Every control flow has its own block whether it's wrapped within the brackets, or just a **valid single statement** mentioned above

            Since **blocks** are used for scope resolution

    3. Or **ends with `;`**

        1. `return;` statement (you can return nothing)
        2. **declaration** statement to be talked about below
        3. `;` is also a valid statement

9. The variable definition takes traditional C form, with corresponding scope resolution

    1. `int a;` will define the variable `a` as uninitialized memory space

    2. `int a = 1;` will define the variable `a`, and initialize it to `1`

    3. `int a = 1, b = 2` will define both `a` and `b` and individually initialize them as specified by the user

        On a grammar level, this is expanded to be a bunch of variable definition and initialization to avoid a deep traversal into the actual AST

        *This optimization would be later illustrated in better detail in the next section*

10. Every **block** of statements indicates a new name scope, whose resolution will be later talked about in the [Code Generation](#Code Generation) section

    *This optimization would be later illustrated in better detail in the next section*

11. An expression falls in the following group:

     1. **Binary Operations**: left hand side and right hand size operated by the operator

     2. **Unary Operations**: a single operator acted upon some other expression

         We use **assignment operation** to simplify the use of `++`, `--` unary operators

         These're simply reconstructed to `a = a + 1` (with assignment operation returning the assigned values)

         *This optimization would be later illustrated in better detail in the next section*

     3. **Ternary Operation(s)**: currently only supporting `?:` as ternary operators

     4. **Assignment Expression**: the assignment of some `ID` or a dereferenced valid pointer `*(a+3)`, typically referred to as *left values*

         Specific operators and their corresponding operations/precedence are defined in [Lexical Analysis](#Lexical Analysis) sections

         Note that we define the grammar from a **low to high** precedence order to account for their ambiguous order and associativity if not carefully specified.

         - Note that **compound assignment** operations can be easily comprehended as a corresponding expression with a regular assignment operation: `<<=` `+=` `-=`, etc.

             *This optimization would be later illustrated in better detail in the next section*

     5. **Function Calls** in the form of `ID(expression list)`

         You can also specify **no parameter**

     6. **Array Subscription** in the form of `ID[expression]`

         In array definition (not an expression), you can also specify a set of empty bracket pairs, indicating a so-called "multidimensional array"

         **Although they're expected to be allocated as a continuous blob in the runtime memory**

12. Expressions can be grouped by `(` and `)` to indicate their correspondence

     As long as the grammar is unambiguous in this section, the programmer should be able to define arbitrarily complex expressions

13. Expressions should also able to be downgraded to some specific stuff:

     1. `ID` for identifiers, this can be variables or functions names
     2. **integer constant** for some literal integers
     3. **float constant** for some floating points
     4. **character constant** wrapped with `''`
     5. **string constant** wrapped with `""`

14. We restrict that only **Unary Operation** can be used at the left side of an assignment. Though this restriction is far from achieving a true **valid left value** check, it would surely make the process of type checking less painful

     *This optimization would be later illustrated in better detail in the next section*

### BNF Definition for the Nano C Language

According to the above grammar specification, we define the following BNF grammars to recognize the specific token patterns

1. We used the careful ordering of grammar production to support complex precedence
2. We inherited the line number and column identification from **tokens** to give some comprehensive error message
3. BNF are written in a nest-able form, allowing for easy recognition of recursively nested grammar

```python
"""
Grammars written here is for you (the human reading this) to have a comprehensive understanding of the NanoC language. They're written in BNF for better copy-pasting compability for the parser, and it should be just the same as the ones used in the parser to build the AST.

Productions used in the parser:

        program             : program function
                            | program declaration
                            |
        function            : type id LPAREN param_list RPAREN curl_block
        param_list          : type id comma_paramters
                            | VOID
                            |
        comma_params        : comma_params COMMA type id
                            |
        block               : block curl_block
                            | block statement
                            | 
        id                  : ID
        type                : INT
                            | VOID
                            | LONG
                            | FLOAT
                            | DOUBLE
                            | CHAR
                            | type TIMES
        statement           : expression SEMI
                            | declaration
                            | IF LPAREN expression RPAREN ctrl_block ELSE ctrl_block
                            | IF LPAREN expression RPAREN ctrl_block
                            | FOR LPAREN for_init RPAREN ctrl_block
                            | WHILE LPAREN expression RPAREN ctrl_block
                            | DO ctrl_block WHILE LPAREN expression RPAREN SEMI
                            | RETURN empty_or_exp SEMI
                            | BREAK SEMI
                            | CONTINUE SEMI
                            | SEMI
        for_init            : empty_or_exp SEMI empty_or_exp SEMI empty_or_exp
                            | declaration empty_or_exp SEMI empty_or_exp
        exp_list            : expression comma_exps
                            |
        comma_exps          : comma_exps COMMA expression
                            |
        empty_or_exp        : expression
                            | 
        ctrl_block          : curl_block
                            | statement
        curl_block          : LBRACE block RBRACE
        declaration         : type dec_list SEMI
        dec_list            : dec_list COMMA id array_list typeinit
                            | id array_list typeinit
        typeinit            : EQUALS expression
                            | 
        array_list          : array_list LBRACKET INT_CONST_DEC RBRACKET
                            |
        expression          : assignment
        assignment          : conditional
                            | unary EQUALS expression
        conditional         : logical_or
                            | logical_or CONDOP expression COLON conditional
        logical_or          : logical_and
                            | logical_or LOR logical_and
        logical_and         : bitwise_or
                            | logical_and LAND bitwise_or
        bitwise_or          : bitwise_xor
                            | bitwise_or OR bitwise_xor
        bitwise_xor         : bitwise_and
                            | bitwise_xor XOR bitwise_and
        bitwise_and         : equality
                            | bitwise_and AND equality
        equality            : relational
                            | equality (EQ|NE) relational
        relational          : shiftable
                            | relational (LT|GT|LE|GE) shiftable
        shiftable           : additive
                            | shiftable (LSHIFT|RSHIFT) additive
        additive            : multiplicative
                            | additive (PLUS|MINUS) multiplicative
        multiplicative      : unary
                            | multiplicative (TIMES|DEVIDE|MOD) unary
        unary               : postfix
                            | (PLUS|MINUS|NOT|LNOT|TIMES|AND|PLUSPLUS|MINUSMINUS) unary
                            | LPAREN type RPAREN unary
        postfix             : primary
                            | id LPAREN exp_list RPAREN
                            | postfix LBRACKET expression RBRACKET
                            | id PLUSPLUS
                            | id MINUSMINUS
        primary             : INT_CONST_DEC
                            | FLOAT_CONST
                            | CHAR_CONST
                            | STRING_LITERAL
                            | id
                            | LPAREN expression RPAREN
"""
```

As mentioned above, we used the `ply` package for token/syntax recognition

With a well-defined grammar, the next step is to parse corresponding production into a well-organized **Abstract Syntax Tree**, which will be illustrated in more detail in the following section

Being an **abstract** syntax tree, a large portion of the parsing is simply to define which production results in which kind of tree node, and how those nodes are to be organized correctly

```python
#############################################################
#                  Arithmetic/Logical Operations            #
#############################################################

def p_binary_operators(self, p):
    '''
    logical_or          : logical_or LOR logical_and
    logical_and         : logical_and LAND bitwise_or
    bitwise_or          : bitwise_or OR bitwise_xor
    bitwise_xor         : bitwise_xor XOR bitwise_and
    bitwise_and         : bitwise_and AND equality
    equality            : equality EQ relational
                        | equality NE relational
    relational          : relational LT shiftable
                        | relational GT shiftable
                        | relational GE shiftable
                        | relational LE shiftable
    shiftable           : shiftable LSHIFT additive
                        | shiftable RSHIFT additive
    additive            : additive PLUS multiplicative
                        | additive MINUS multiplicative
    multiplicative      : multiplicative TIMES unary
                        | multiplicative DIVIDE unary
                        | multiplicative MOD unary
    '''
    p[0] = BinaryNode(p[2], p[1], p[3])

```

Take this binary operation parsing as an example:

- The precedence are defined within the grammar itself

- The actual operator takes similar form (a string of one/two special character indicating a specific operation)

- Nested parenthesis pairs and the actual positioning (where these operations should appear) of those operations are well defined into the **tree-structure** (*the parse tree*)

- Boiling down to the AST building, all we have to do is construct the AST node and store it for later (upper in the parse tree)

    ```python
    p[0] = BinaryNode(p[2], p[1], p[3])
    ```

Thanks to the parse tree, `p[1]`, `p[2]`, `p[3]` are already valid elements of the AST (constructed in the parsing process before this one and saved to the **parsed object `p[0]`**)

For example, some consecutive parsing of binary operations (`LPAREN` and `RPAREN` taken care of, omitted here) might be flattened like this:

```python
p[0] = BinaryNode(BinaryNode(BinaryNode(p[2], p[1], BinaryNode(p[2], p[1], p[3])), p[1], p[3]), p[1], BinaryNode(BinaryNode(p[2], p[1], p[3]), p[1], BinaryNode(p[2], p[1], p[3])))
```





### Specific Optimizations

## Abstract Syntax Tree

### Tree Node Design

### Tree Traversal (Optimization)

### Side Note: Python Hosted Server

### Tree Visualization and Interaction

## Code Generation

### LLVM Intermediate Representation

### Specific Optimization

## Compilation

### IR to Assembly

### Assembling the Executable

## References

- [PyCParser](https://github.com/eliben/pycparser)
- ...
