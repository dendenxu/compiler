# Nano C Compiler

The C programming language compiler with extremely limited functionality.

We'd only implement a subset of a subset of C. Don't even expect preprocessing.

And **do remember to delete these lines after this repo goes public**

## Lexical Analysis

### Token Specification

- Types: `int`, `long`, `double`, `float`, `char`, `void`, `[]`, **pointer**
- Control Flow: `if`, `else`, `while`, `for`, `continue`, `break`, `do-while`
- Function: `return`, **typed functions**, **scope**(`{}` `;`)
- Operators (with priorities):
    1. `()` `[]`  Function Call, Array Subscription
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
        14. `=` `<<=` `>>=` `&=` `~=` `^=` `+=` `-=` `/=` `*=` `%=` Assignment Operation
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



To help the user pinpoint what's gone wrong the tokenization process, we "remembers" every token's location (in terms of line number and token column), which will even be used in the later syntax analysis process.

### Specific Optimizations





## Syntax Analysis

### Context Free Grammar for Nano C language

### Specific Optimizations





## Abstract Syntax Tree

### Tree Node Design

### Tree Traversal (Optimization)

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
