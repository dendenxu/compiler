

![校标](readme.assets/校标.svg)

<center><strong style="font-size: 1.8em">Zhejiang Unversity Experiment Report</strong></center>



- **Course Name:** Compile Principle
- **Student Name:** Feng Xiang, Wang Junzhe, Xu Zhen
- **Student ID:** 3180103426, 3180103011, 3180105504
- **Department:** Computer Science & Technology
- **Major:** Computer Science & Technology
- **Instructor:** Feng Yan



[toc]

# Nano C Compiler

The C programming language compiler with extremely limited functionality:smile:

Visit [the tree visualizer](http://neon-cubes.xyz:8000/src/nanoast.html) to see what abstract tree the developer is lately developing.

Usage:

```shell
# This will: read the source code, get tokens, generate parse tree, generate AST, send AST to server, emit IR, store IR to file, compile IR to Assembly, compile Assembly to Executable
python src/nanoirgen.py -i <input_file_path> -o <output_IR_path> -g
# Executable/Assemble file names/path are derived from <output_IR_path>
```

Example:

```shell
# under folder: compiler
python src/nanoirgen.py -i samples/quicksort.c -o results/quicksort.ll -g -e .exe
# executable saved at: ./results/

# run the executable
./results/quicksort.exe

# check output (in return values)
echo $lastExitCode

# if you see 1, the code works (see ./samples/quicksort.c)
# if you see 0, the code failed to quicksort
```

More usage about `nanoirgen.py` and `nanoyacc.py`

```shell
# python src/nanoirgen.py -h
usage: nanoirgen.py [-h] [-input INPUT] [-output OUTPUT] [-target TARGET] [-url URL] [-tree TREE] [-generate] [-ext EXT]

optional arguments:
  -h, --help      show this help message and exit
  -input INPUT
  -output OUTPUT
  -target TARGET
  -url URL
  -tree TREE
  -generate       Whether to generate the target machine code
  -ext EXT        Executable file extension
```

```shell
# python src/nanoyacc.py -h
usage: nanoyacc.py [-h] [-input INPUT] [-tree TREE] [-url URL]

optional arguments:
  -h, --help    show this help message and exit
  -input INPUT
  -tree TREE
  -url URL
```

<center><strong style="font-size: 1.8em">If You're Viewing the PDF Format of This File</strong></center>

==IMPORTANT: To better grasp the ability of our Abstract Syntax Tree visualizer, go to the [GitHub](https://github.com/dendenxu/compiler) of this repo to see for yourself.==

==IMPORTANT: The visualizer is hosted at: [my server](http://neon-cubes.xyz:8000/src/nanoast.html)==



## Chapter 1 - Lexical Analysis

### §1.1 Token Specification

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

### §1.2 Token Definition

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

We used the `PLY` (Python Lex Yacc) to help better recognize regular expressions and BNF grammars to make our life easier.

We only need to import the "lexer" from the PLY module using `from ply import lex`

And build it with `lex.build`, passing specific module into the build function.

The lexer utilizes Python's object reflection (introspection) so it needs the current building context to extract regular expressions and map them to corresponding tokens.

It mainly recognize variables defined as `t_TOKEN_NAME`, the content of the variable corresponds to the regular expression, and the `TOKEN_NAME` part would be the token this RE recognizes for.

### §1.3 Specific Optimizations

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

To help the user pinpoint what's gone wrong the tokenization process, `PLY` "remembers" every token's location (in terms of line number and token column), which will even be used in the later syntax analysis process.

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

## Chapter 2 - Syntax Analysis

### §2.1 Grammar Syntax for Nano C language

Firstly, let's take a comprehensive look at our grammar:

1. We _don't_ implement preprocessing like **macros** and **includes**

   - You **cannot** `#define` or `#include`

2. We _don't_ implement multi-file compilation, as a direct cause of the first rule

   - You **cannot** `python nanoirgen.py a.c b.c c.c -o a.out`

3. Thus we want a program to define the whole program (a single C source file)

4. This program should contain some **global variable definitions**

5. This program should also contain some **function definitions**

6. We _don't_ support **external linkage** variable definitions due to rule number one

7. We _don't_ support function/global variable **declaration**s since it won't be of much use in this setup.

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

         `while (1) while(0) while(controller) do p = "inside while loop"; while ( condition == "OK" );`

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

      _This optimization would be later illustrated in better detail in the next section_

   4. Note that type node should only be declared once in one declaration statement or declaration list, meaning `int * a, * b` is illegal, while `int *********** a, b, c=1, d` is OK

10. Every **block** of statements indicates a new name scope, whose resolution will be later talked about in the [Code Generation](#Chapter 5 - Code Generation) section

    _This optimization would be later illustrated in better detail in the next section_

11. An expression falls in the following group:

    1. **Binary Operations**: left hand side and right hand size operated by the operator

    2. **Unary Operations**: a single operator acted upon some other expression

       We use **assignment operation** to simplify the use of `++`, `--` unary operators

       These're simply reconstructed to `a = a + 1` (with assignment operation returning the assigned values)

       _This optimization would be later illustrated in better detail in the next section_

    3. **Ternary Operation**(s): currently only supporting `?:` as ternary operators

    4. **Assignment Expression**: the assignment of some `ID` or a dereferenced valid pointer `*(a+3)`, typically referred to as _left values_

       Specific operators and their corresponding operations/precedence are defined in [Lexical Analysis](#Chapter 1 - Lexical Analysis) sections

       Note that we define the grammar from a **low to high** precedence order to account for their ambiguous order and associativity if not carefully specified.

       - Note that **compound assignment** operations can be easily comprehended as a corresponding expression with a regular assignment operation: `<<=` `+=` `-=`, etc.

         _This optimization would be later illustrated in better detail in the next section_

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

    _This optimization would be later illustrated in better detail in the next section_

### §2.2 BNF Definition for the Nano C Language

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

As mentioned above, we used the `PLY` package for token/syntax recognition

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

- Nested parenthesis pairs and the actual positioning (where these operations should appear) of those operations are well defined into the **tree-structure** (_the parse tree_)

- Boiling down to the AST building, all we have to do is construct the AST node and store it for later (upper in the parse tree)

  ```python
  p[0] = BinaryNode(p[2], p[1], p[3])
  ```

Thanks to the parse tree, `p[1]`, `p[2]`, `p[3]` are already valid elements of the AST (constructed in the parsing process before this one and saved to the **parsed object `p[0]`**)

For example, some consecutive parsing of binary operations (`LPAREN` and `RPAREN` taken care of, omitted here) might be flattened like this:

```python
p[0] = BinaryNode(BinaryNode(BinaryNode(p[2], p[1], BinaryNode(p[2], p[1], p[3])), p[1], p[3]), p[1], BinaryNode(BinaryNode(p[2], p[1], p[3]), p[1], BinaryNode(p[2], p[1], p[3])))
```

A nice visualization of this might be like:

![binaryop](readme.assets/binaryop.svg)

### §2.3 Actual Implementation

```python
#############################################################
#                      Syntax Error Rules                   #
#############################################################

def p_error(self, p):
    # with a syntax error, the token should contain corresponding location
    print(colored("Error: ", "red")+"Syntax error when parsing "+str(p))

#############################################################
#                      External Functions                   #
#############################################################

def parse(self, input, **kwargs) -> Node:
    try:
        return self.parser.parse(input, **kwargs)
    except Exception as e:
        traceback.print_exc()
        print(colored("Error: ", "red")+f"{e}")

def build(self, **kwargs):
    self.parser = yacc.yacc(module=self, **kwargs)

tokens = NanoLexer.tokens
```

Similar to the lexer, `yacc` needs to be specifically built for using.

We pass in `module=self` to make YACC track production definition in current object scope using object reflection.

```python
tokens = NanoLexer.tokens
```

is needed to define valid tokens to recognize for (usually marked UPPER CASE CHARACTER).

To make the parsing process more visible and viable, we defined the main function of the `nanoyacc.py` program as this:

```python
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-input", default="samples/fx.c", type=str)
    parser.add_argument("-tree", type=str)
    parser.add_argument("-url", default="http://neon-cubes.xyz:8000/src/tree.json", type=str)
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        lexer.build()
        parser = NanoParser()
        parser.build()
        root = parser.parse(content, debug=0)
        print(colored(f"Abstract Syntax Tree:", "yellow", attrs=["bold"]))
        print(root)

        tree = traverse(root)
        print(colored("Structrued Tree: ", 'yellow', attrs=['bold']))
        print(tree)
        addinfo(tree, args.input)
        payload = json.dumps(tree)

        if args.tree:
            with open(args.tree, 'w') as f:
                f.write(payload)
            print(colored(f"Saved Structrued Tree to {args.tree}", 'yellow', attrs=['bold']))

        r = requests.post(url=args.url, data=payload)
        print(colored(f"POST response: {r}", "yellow", attrs=["bold"]))
```

1. `argparse` exists so we have a friendly command-line interface for the **nanoparser**
2. `lexer` is built and automatically stored in a safe position (a global variable `ply.lex.lexer`)
3. `parser` is also built and automatically stored in a safe position `ply.yacc.parser`
4. `root` is returned by the parser as the root of the AST, to be used by the intermediate representation generator
5. `tree` is the simplified version (ready to be displayed with good visual look)
6. We set up a server to receive the AST JSON object for mobility and compatibility for the visualization of the AST nodes
7. `colored` from `termcolor` is applied extensively to give a visually pleasant command-line output
8. `tree.json` will also be saved as a file for inspection

### §2.4 Specific Optimizations

#### Flattening

We flatten declaration operations to make the actual IR generation a little bit less painful.

- Given a list of declarations, initialized or not, we flatten all declarations into individual statements, so the compiler backend can uniformly take care of them

  `int a, b, c;` would initially produce a list of declaration as `[DecNode, DecNode, DecNode]`

  When the outer block is encountered, those expressions are flattened out as

  `DecNode; DecNode; DecNode;`

- This is implemented with the help of `BlockNode`

  ```python
  def p_block_stmt(self, p):
      '''
      block               : block curl_block
                          | block statement
      '''
      if p[1] is None:
          p[1] = BlockNode()
      if isinstance(p[2], list):
          for dec in p[2]:
              p[1].append(dec)
      else:
          p[1].append(p[2])
      p[0] = p[1]
  ```

The above implementation also illustrates other implementation of flattening listed grammar

```python
'''
    block               : block curl_block
                        | block statement
                        |
'''
```

is **left recursive**, thus the first block might just be `None`, and later all other blocks should be appended accordingly to whether we've already constructed a list from the first element.

Similar optimization occurs when we're parsing **expression list** of function call/**parameter list** of function definition

- **Expression List** in function call:

  ```python
  def p_exp_list(self, p):
      '''
      exp_list            : expression comma_exps
      '''
      if p[2] is None:
          p[2] = []
      p[2] = [p[1]] + p[2]
      p[0] = p[2]

  def p_comma_exp_list(self, p):
      '''
      comma_exps          : comma_exps COMMA expression
      '''
      if p[1] is None:
          p[1] = []
      p[1].append(p[3])
      p[0] = p[1]
  ```

- **Parameter List** in function definition

  ```python
  #############################################################
  #                     Function Definition                   #
  #############################################################
  
  def p_func_def(self, p):
      '''
      function            : type id LPAREN param_list RPAREN curl_block
      '''
      p[0] = FuncNode(p[1], p[2], p[4], p[6])
  
  def p_params(self, p):
      '''
      param_list          : type id comma_params
      '''
      param = ParamNode(p[1], p[2])
      if p[3] is None:
          p[3] = []
      p[3] = [param] + p[3]
      p[0] = p[3]
  
  def p_comma_params(self, p):
      '''
      comma_params        : comma_params COMMA type id
      '''
      param = ParamNode(p[3], p[4])
      if p[1] is None:
          p[1] = []
      p[1].append(param)
      p[0] = p[1]
  ```

#### Preparations for Scope Resolution

Every **block** of statements indicates a new name scope, whose resolution will be later talked about in the [Code Generation](#Chapter 5 - Code Generation) section

Note that `BlockNode` is **_ABSTRACT_**, meaning with the total removal of it, the compiler should still be able to work properly. The purpose of the aggregated node is to indicate nested scope creation

- Thus, when parsing curly brackets pairs, we explicitly generate a `BlockNode` to mark the creation of a new scope

- We also took care of `if-else-stmt` and `for-do-while-loop` statements, whose statement body is valid even when they've only got one individual statement

  Those individual statement are also wrapped with an abstract `BlockNode`

#### Abstraction of Complex Syntax

For the compiler backend, `a += 1` is the same as `a = a + 1` and in our implementation, `a++` or `++a`

So, when implementing similar relatively complex grammar, the parser automatically translates it to the format that the compiler recognizes

Thus a simple `AssNode` (meaning, `Assignment Node`) can take care of all of these and free the IR from recognizing complex assignment and syntax sugar

This is implemented as:

```python
def p_assignment(self, p):
    '''
    assignment          : unary EQUALS expression
                        | unary TIMESEQUAL expression
                        | unary DIVEQUAL expression
                        | unary MODEQUAL expression
                        | unary PLUSEQUAL expression
                        | unary MINUSEQUAL expression
                        | unary LSHIFTEQUAL expression
                        | unary RSHIFTEQUAL expression
                        | unary ANDEQUAL expression
                        | unary XOREQUAL expression
                        | unary OREQUAL expression
    unary               : PLUSPLUS unary
                        | MINUSMINUS unary
    postfix             : postfix PLUSPLUS
                        | postfix MINUSMINUS

    '''
    if len(p) == 4:
        if len(p[2]) == 1:  # true assignment
            p[0] = AssNode(p[1], p[3])
        else:
            if len(p[2]) == 3:
                op = p[2][:2]
            else:
                op = p[2][:1]
            p[0] = AssNode(p[1], BinaryNode(op, p[1], p[3]))

    else:
        if p[1] == "++":
            p[0] = AssNode(p[2], BinaryNode('+', p[2], IntNode(1)))
        elif p[1] == "--":
            p[0] = AssNode(p[2], BinaryNode('-', p[2], IntNode(1)))
        elif p[2] == "++":
            p[0] = AssNode(p[1], BinaryNode('+', p[1], IntNode(1)))
        elif p[2] == "--":
            p[0] = AssNode(p[1], BinaryNode('-', p[1], IntNode(1)))
        p[0].exp.update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))
    p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))
```

#### Trick for Solving the Dangling Else Problem

The dangling else problem in grammar syntax parsing appears when no restriction is applied on the end of if statement

with a grammar definition like:

```python
 '''
    statment                   : IF LPAREN expression RPAREN ctrl_block ELSE ctrl_block
                               | IF LPAREN expression RPAREN ctrl_block
 '''
```

and a program like this:

```python
if (1) if (2) ; else ;
```

The else can be associated with the first `if` like with brackets:

```python
if (1) { if (2) ; } else ;
```

Or the second `if`:

```python
if (1) { if (2) ; else ; }
```

**without violating the grammar definition**!

This is commonly known as _the dangling else_ problem:

- Whether and else statement should be paired with the outer most if statement or the inner most unpaired one?

There's an ugly solution to this:

- Define the grammar so that **only unmatched statement** can be associated with the if statement

  ```python
  '''
  statement                : matched-stmt | unmatched-stmt
  matched-stmt             : if  ( exp ) matched-stmt else matched-stmt
                           | other
  unmatched-stmt           : if  ( exp ) statement
                           | if  ( exp ) matched-stmt else unmatched-stmt
  exp                      : 0 | 1
  '''
  ```

  > **This works by permitting** only a matched-statement to come before an else in an if-statement**, thus forcing all else-parts to be matched as soon as possible.**

  But this solution would require some painful modification of the parser code

- And another solution would be marking the end of the if-else block with some special token like `end-if`

  ```python
  if (1) ; else ; endif
  ```

  Effectively acting as a pair (pairs) of curly brackets

  solving the ambiguity by make the programmer do more

- The **most popular** solution is to actually leave the grammar be

  Leave everything be and let the **LALR** parser **prefer shift over reduce** when there's a shift-reduce conflict

  And this is also the solution that we used

  ```plaintext
  ...
  ...
  state 196
  
      (17) statement -> IF LPAREN expression RPAREN ctrl_block .
      (18) statement -> IF LPAREN expression RPAREN ctrl_block . ELSE ctrl_block
  
    ! shift/reduce conflict for ELSE resolved as shift
      ELSE            shift and go to state 202
  
    ! ELSE            [ reduce using rule 17 (statement -> IF LPAREN expression RPAREN ctrl_block .) ]
  ...
  ...
  WARNING:
  WARNING: Conflicts:
  WARNING:
  WARNING: shift/reduce conflict for ELSE in state 196 resolved as shift
  ```

  > If the parser is produced by an SLR, LR(1) or LALR [LR parser](https://en.wikipedia.org/wiki/LR_parser) generator, the programmer will often rely on the generated parser feature of preferring shift over reduce whenever there is a conflict.[[2\]](https://en.wikipedia.org/wiki/Dangling_else#cite_note-Bison_Manual-2) Alternatively, the grammar can be rewritten to remove the conflict, at the expense of an increase in grammar size

## Chapter 3 - Abstract Syntax Tree

### §3.1 Node Design

We adopted the OOP design pattern to make life easier for `pylance`, the type checking utility and auto-complete functionality of the developer's IDE

`Node` is defined to be the base class of every node and this type can be used to distinguish an actual `NanoAST` node from some string/number literals and original python literals like `list`s or `dict`s.

Specifically, We have

- A base class `Node` for all AST nodes

- A base class `EmptyStmtNode` sub-classing `Node`, acting as base class of all primitive statements, including

  - `IfStmtNode`
  - `LoopNode` for all looping including
    - `FOR` loop
    - `WHILE` loop
    - `DO-WHILE` loop
  - `DecNode`
  - `RetNode`
  - `BlockNode` for aggregating all other statements
  - `BreakNode`
  - `ContinueNode`

  Note that an `Expression` followed by a `SEMI` (semicolon) is also a valid statement, but for **abstraction**, we extract that to be able to be directly embedded in `BlockNode`

- A base class `EmptyExpNode` sub-classing `Node`, acting as base class of all primitive expressions, including

  - `CallNode` for function call
  - `UnaryNode` for unary operations
  - `BinaryNode` for binary operations
  - `TernaryNode` for ternary operations
  - `AssNode` for assignment expressions
  - `ArrSubNode` for subscription of an array/pointer

### §3.2 Tree Visualization and Interaction

==IMPORTANT: To better grasp the ability of our Abstract Syntax Tree visualizer, go to the [GitHub](https://github.com/dendenxu/compiler) of this repo to see for yourself.==

==IMPORTANT: The visualizer is hosted at: [my server](http://neon-cubes.xyz:8000/src/nanoast.html)==

On the hosted server mentioned above, we have a nice little html (including some `javascript`) to display the abstract syntax tree in an understandable and **interactive** manner.

If you're able to see the moving GIF, I don't think I need to explain more.

If you're seeing a static image, please read the `IMPORTANT` message a few lines above.

![ast](readme.assets/ast.gif)

The server is also designed to accept incoming compilation, so you can basically update what to display to everyone by uploading the `tree.json` traversed to the server.

Implementation:

```python
tree = traverse(root)
addinfo(tree, args.input)
# Print Struct Tree (data sent to server)
print(colored("Structrued Tree: ", 'yellow', attrs=['bold']))
print(tree)
payload = json.dumps(tree)

if args.tree:
    with open(args.tree, 'w') as f:
        f.write(payload)
        print(colored(f"Saved Structrued Tree to {args.tree}", 'yellow', attrs=['bold']))

r = requests.post(url=args.url, data=payload)
print(colored(f"POST response: {r}", "yellow", attrs=["bold"]))
```

![ast_compile](readme.assets/ast_compile.gif)

You're also able to download a fully viewable tree from the server directly (or rather, from the `nanoast.html` you're visiting)

![download_svg](readme.assets/download_svg.gif)

You'll see similar **SVG** embedded in our report later in the Code Generation section.

### §3.3 Optimization Considerations

#### Better Debugging Interface

When designing the base class of all nodes, we considered the need to pretty print all things from command-line, thus a `indentLevel` is added and all `__str__` methods of nodes are designed to recursively do a depth first search on the abstract syntax tree to produce some human readable parsing results (with formats!)

```python
class Node(object):
    # A simple Abstract Syntax Tree node
    TABSTR = '|   '

    def __init__(self):
        self._indentLevel = 0
        self._lineno = self._colno = 0

    def update_pos(self, line: int, col: int):
        self._lineno = line
        self._colno = col

    def accept(self, visitor: NanoVisitor):
        pass
```

![image-20210606202857114](readme.assets/image-20210606202857114.png)

Also, with error message in mind, we printed detailed line numbering and column to help the compiler user location where things might have gone wrong as early as possible.

```c
int main()
{
    { ret
    }
}
```

![image-20210606203341832](readme.assets/image-20210606203341832.png)

```c
int main()
{
    if (if)
}
```

![image-20210606203509676](readme.assets/image-20210606203509676.png)

Correct warning location during later phases:

This is the source for a simple quicksort algorithm

```c
/**
 * feature:
 *      integer type & float type & void type
 *      pointer type & array type
 *      & and * operator
 *      type casting:
 *          xd array -> pointer
 *          int <-> float
 *      calculations:
 *          *(pointer + integer)
 *      quicksort
 *      random integer generation
 * expected output: 1
 */

int qsort(int *a, int l, int r)
{
    int i = l;
    int j = r;
    int p = *(a + ((l + r) / 2));
    int flag = 1;
    while (i <= j) {
        while (*(a + i) < p) i++;
        while (*(a + j) > p) j--;
        if (i > j) break;
        int u = *(a + i);
        *(a + i) = *(a + j);
        *(a + j) = u;
        i++;
        j--;
    }
    if (i < r) qsort(a, i, r);
    if (j > l) qsort(a, l, j);
    return 0;
}

// random floating point number distributed uniformly in [0,1]
float rand(float *r)
{
    float base = 256.0;
    float a = 17.0;
    float b = 139.0;
    float temp1 = a * (*r) + b;
    float temp2 = (float)(int)(temp1 / base);
    float temp3 = temp1 - temp2 * base;
    *r = temp3;
    float p = *r / base;
    return p;
}

int initArr(int *a, int n)
{
    float state = 114514.0;
    int i = 0;
    while (i < n) {
        *(a + i) = (int)(255 * rand(&state));
        i += 1;
    }
}

int isSorted(int *a, int n)
{
    int i = 0;
    while (i < n - 1) {
        if ((*(a + i)) > (*(a + i + 1)))
            return 0;
        i += 1;
    }
    return 1;
}

int main()
{
    int n = 100;
    int arr[100];
    int *a = (int *)arr;
    initArr(a, n);
    qsort(a, 0, n - 1);
    return isSorted(a, n);
}
```

With the help of carefully designed line number/column memory and the help of a tracking parser, it's easy for the user to locate the erroneous code.

![image-20210606211234698](readme.assets/image-20210606211234698.png)

#### Better Coding

We adopted the OOP design pattern to make life easier for `pylance`, the type checking utility and auto-complete functionality of the developer's IDE

Before, you might need to check whether a node is valid by comparing some raw string:

```python
if node.name == "StmtNode": pass
```

This design makes the compiler writer get trapped in the pitfall of **typos**.

Now you only need to do

```python
if isinstance(node, StmtNode): pass
```

or

```python
if type(node) == StmtNode: pass
```

Writing things out explicitly makes the checker's life, and your life much easier by providing richer error messages.

I believe you've all had that afternoon spent digging into your code trying to find which tiny typo crashed your delicate, complex, strong program.

`Node` is defined to be the base class of every node and this type can be used to distinguish an actual `NanoAST` node from some string/number literals and original python literals like `list`s or `dict`s.

## Chapter 4 - Semantic Analysis

### §4.1 Name Resolution

During compilation, our compiler associates identifiers such as the name of a variable with an address (memory location), datatype, or actual value. This process is called _binding_. The association lasts through all subsequent executions until a recompilation occurs, which might cause a rebinding. Before binding the names, our compiler must resolve all references to them in the compilation unit. This process is called _name resolution_ Cour compiler considers all names to be in the same namespace. So, one declaration or definition in an inner scope can hide another in an outer scope.

#### Scope Checking

```python
    def _get_identifier(self, name):
        for d in self.scope_stack[::-1]:  # reversing the scope_block
            if name in d:
                return d[name]['ref']
        return None
```

We use a scope stack to store the different symbol tables. We will recursively checking the scope from the last created scope to the oldest scope which is known as most recent variable matching rule.

#### Binding Reference With Name

```python
def _add_identifier(self, name, reference, type):
        if self.scope_stack == []:
            return None
        if name in self.scope_stack[-1]:
            return None
        self.scope_stack[-1][name] = {'ref': reference, 'typ': type}
        return self.scope_stack[-1][name]
```

As we already have a scope stack, we can set the binding between name and reference by a python `dict` object and add the key-value to the latest scope.

### §4.2 Type Checking (L value Checking)

Type checking happens at many places and operations. For binary operation, we need to check that the left type and the right type is compatible. We use a survey to illustrate compatible rules and return type:

```python
binCompatDict = {
    #left       right      op       ret_type
    ('i32',     'i32',     '+' ):   'i32',
    ('i32',     'i32',     '-' ):   'i32',
    ('i32',     'i32',     '*' ):   'i32',
    ('i32',     'i32',     '/' ):   'i32',
    ('i32',     'i32',     '%' ):   'i32',
    ('i32',     'i32',     '<<'):   'i32',
    ('i32',     'i32',     '>>'):   'i32',
    ('i32',     'i32',     '!='):   'i1',
    ('i32',     'i32',     '=='):   'i1',
    ('i32',     'i32',     '<' ):   'i1',
    ('i32',     'i32',     '>' ):   'i1',
    ('i32',     'i32',     '<='):   'i1',
    ('i32',     'i32',     '>='):   'i1',
    ('i32',     'i32',     '||'):   'i1',
    ('i32',     'i32',     '&&'):   'i1',
    ('float',   'float',   '+' ):   'float',
    ('float',   'float',   '-' ):   'float',
    ('float',   'float',   '*' ):   'float',
    ('float',   'float',   '/' ):   'float',
    ('float',   'float',   '%' ):   'float',
    ('float',   'float',   '!='):   'i1',
    ('float',   'float',   '=='):   'i1',
    ('float',   'float',   '<' ):   'i1',
    ('float',   'float',   '>' ):   'i1',
    ('float',   'float',   '<='):   'i1',
    ('float',   'float',   '>='):   'i1',
    ('float',   'float',   '||'):   'i1',
    ('float',   'float',   '&&'):   'i1',
    ('i1',      'i1',      '+' ):   'i32',
    ('i1',      'i1',      '-' ):   'i32',
    ('i1',      'i1',      '*' ):   'i32',
    ('i1',      'i1',      '/' ):   'i32',
    ('i1',      'i1',      '%' ):   'i32',
    ('i1',      'i1',      '!='):   'i1',
    ('i1',      'i1',      '=='):   'i1',
    ('i1',      'i1',      '<' ):   'i1',
    ('i1',      'i1',      '>' ):   'i1',
    ('i1',      'i1',      '<='):   'i1',
    ('i1',      'i1',      '>='):   'i1',
    ('i1',      'i1',      '||'):   'i1',
    ('i1',      'i1',      '&&'):   'i1',
    ('i32',     'i1',      '+' ):   'i32',
    ('i32',     'i1',      '-' ):   'i32',
    ('i32',     'i1',      '*' ):   'i32',
    ('i32',     'i1',      '/' ):   'i32',
    ('i32',     'i1',      '%' ):   'i32',
    ('i32',     'i1',      '!='):   'i1',
    ('i32',     'i1',      '=='):   'i1',
    ('i32',     'i1',      '<' ):   'i1',
    ('i32',     'i1',      '>' ):   'i1',
    ('i32',     'i1',      '<='):   'i1',
    ('i32',     'i1',      '>='):   'i1',
    ('i32',     'i1',      '||'):   'i1',
    ('i32',     'i1',      '&&'):   'i1',
    ('i1',      'i32',     '+' ):   'i32',
    ('i1',      'i32',     '-' ):   'i32',
    ('i1',      'i32',     '*' ):   'i32',
    ('i1',      'i32',     '/' ):   'i32',
    ('i1',      'i32',     '%' ):   'i32',
    ('i1',      'i32',     '!='):   'i1',
    ('i1',      'i32',     '=='):   'i1',
    ('i1',      'i32',     '<' ):   'i1',
    ('i1',      'i32',     '>' ):   'i1',
    ('i1',      'i32',     '<='):   'i1',
    ('i1',      'i32',     '>='):   'i1',
    ('i1',      'i32',     '||'):   'i1',
    ('i1',      'i32',     '&&'):   'i1',
    ('float',   'i32',     '+' ):   'float',
    ('float',   'i32',     '-' ):   'float',
    ('float',   'i32',     '*' ):   'float',
    ('float',   'i32',     '/' ):   'float',
    ('float',   'i32',     '%' ):   'float',
    ('float',   'i32',     '!='):   'i1',
    ('float',   'i32',     '=='):   'i1',
    ('float',   'i32',     '<' ):   'i1',
    ('float',   'i32',     '>' ):   'i1',
    ('float',   'i32',     '<='):   'i1',
    ('float',   'i32',     '>='):   'i1',
    ('float',   'i32',     '||'):   'i1',
    ('float',   'i32',     '&&'):   'i1',
    ('i32',     'float',   '+' ):   'float',
    ('i32',     'float',   '-' ):   'float',
    ('i32',     'float',   '*' ):   'float',
    ('i32',     'float',   '/' ):   'float',
    ('i32',     'float',   '%' ):   'float',
    ('i32',     'float',   '!='):   'i1',
    ('i32',     'float',   '=='):   'i1',
    ('i32',     'float',   '<' ):   'i1',
    ('i32',     'float',   '>' ):   'i1',
    ('i32',     'float',   '<='):   'i1',
    ('i32',     'float',   '>='):   'i1',
    ('i32',     'float',   '||'):   'i1',
    ('i32',     'float',   '&&'):   'i1',
    ('i1',      'float',   '+' ):   'float',
    ('i1',      'float',   '-' ):   'float',
    ('i1',      'float',   '*' ):   'float',
    ('i1',      'float',   '/' ):   'float',
    ('i1',      'float',   '%' ):   'float',
    ('i1',      'float',   '!='):   'i1',
    ('i1',      'float',   '=='):   'i1',
    ('i1',      'float',   '<' ):   'i1',
    ('i1',      'float',   '>' ):   'i1',
    ('i1',      'float',   '<='):   'i1',
    ('i1',      'float',   '>='):   'i1',
    ('i1',      'float',   '||'):   'i1',
    ('i1',      'float',   '&&'):   'i1',
    ('float',   'i1',      '+' ):   'float',
    ('float',   'i1',      '-' ):   'float',
    ('float',   'i1',      '*' ):   'float',
    ('float',   'i1',      '/' ):   'float',
    ('float',   'i1',      '%' ):   'float',
    ('float',   'i1',      '!='):   'i1',
    ('float',   'i1',      '=='):   'i1',
    ('float',   'i1',      '<' ):   'i1',
    ('float',   'i1',      '>' ):   'i1',
    ('float',   'i1',      '<='):   'i1',
    ('float',   'i1',      '>='):   'i1',
    ('float',   'i1',      '||'):   'i1',
    ('float',   'i1',      '&&'):   'i1',
    ('i32*',    'i32',     '+' ):   'i32*',
    ('i32',     'i32*',    '+' ):   'i32*',
    ('float*',  'i32',     '+' ):   'float*',
    ('i32',     'float*',  '+' ):   'float*',
}
```

Notice that some rules will involving implicit type casting. For example `int1` and `int32` by arithemetic operations, we need to implicitly cast `int1` to `int32` which we defined yielding a warning:

```python
    elif exp_type(left) == 'i1' and exp_type(right) == 'i32':
        left.value = tp_visitor._get_builder().zext(val(left), int32)
    elif exp_type(left) == 'i32' and exp_type(right) == 'i1':
        right.value = tp_visitor._get_builder().zext(val(right), int32)
```

```python
 if ret_type != exp_type(left):
        tp_visitor.n_warnings += 1
        print(str(TImplicitCastWarning(exp_type(left), ret_type)) + f" at position (line {left._lineno}, col {left._colno})")
```

Also we can force the expression to do type casting of which the ruls are also defined in a survey:

```python
allowed_casting = [
    ('i1'    , 'i32'  ),
    ('i32'   , 'float'),
    ('i1'    , 'float'),
    ('float' , 'i1'   ),
    ('float' , 'i32'  ),
    ('[@ x i32]*'  , 'i32*'  ),
    ('[@ x float]*', 'float*'),
    ('[@ x [@ x i32]]*'  , 'i32*'  ),
    ('[@ x [@ x float]]*', 'float*'),
    ('[@ x [@ x [@ x i32]]]*'  , 'i32*'  ),
    ('[@ x [@ x [@ x float]]]*', 'float*'),
]
```

For the conversion between int and float:

```python
    elif (src_type, tgt_type) == ('i32', 'float'):
        return tp_visitor._get_builder().sitofp(value, flpt)
    elif (src_type, tgt_type) == ('float', 'i32'):
        return tp_visitor._get_builder().fptosi(value, int32)
```

We support cast 1d/2d/3d-arry to pointers:

```python
    elif (src_type, tgt_type) == ('[@ x i32]*', 'i32*'):
        val = tp_visitor._get_builder().gep(ref, [ir.Constant(int32, 0),
                                                  ir.Constant(int32, 0),])
        return val
    elif (src_type, tgt_type) == ('[@ x [@ x i32]]*', 'i32*'):
        val = tp_visitor._get_builder().gep(ref, [ir.Constant(int32, 0),
                                                  ir.Constant(int32, 0),])
        return tp_visitor._get_builder().bitcast(val, make_ptr(int32))
    elif (src_type, tgt_type) == ('[@ x [@ x [@ x i32]]]*', 'i32*'):
        val = tp_visitor._get_builder().gep(ref, [ir.Constant(int32, 0),
                                                  ir.Constant(int32, 0),
                                                  ir.Constant(int32, 0),
                                                  ir.Constant(int32, 0),])
```

## Chapter 5 - Code Generation

In the previous part, we have already obtained an abstract syntax tree. Then, we need to visit this tree to generate the target code. Of course we can directly generate target code like assembly language from this AST. However, on the consideration of scalability, we will first generate intermediate representation(IR) of this abstract syntax tree and then synthesize target code from this intermediate representation.

As for the generation of intermediate representation, we use a python package named `llvmlite`. `LLVMlite` is a small subset of the LLVM IR that we will be using throughout the course as the intermediate representation in our compiler. Conceptually, it is either an abstract assembly-like language or a even lower-level C-like language that is convenient to manipulate programmatically.

### §5.1 LLVM Intermediate Representation

To give you a sense of structure of `LLVMlite` programs and the most basic features, the following is our running example, the simple recursive factorial function written in the concrete syntax of the `LLVMlite` IR.

```assembly
    define i64 @fac(i64 %n) {              ; (1)
      %1 = icmp sle i64 %n, 0              ; (2)
      br i1 %1, label %ret, label %rec     ; (3)
    ret:                                   ; (4)
      ret i64 1
    rec:                                   ; (5)
      %2 = sub i64 %n, 1                   ; (6)
      %3 = call i64 @fac(i64 %2)           ; (7)
      %4 = mul i64 %n, %3
      ret i64 %4                           ; (8)
    }

    define i64 @main() {                   ; (9)
      %1 = call i64 @fac(i64 6)
      ret i64 %1
    }
```

First, notice the function definition at (1). The i64 annotations declare the return type and the type of the argument n. The argument is prefixed with "%" to indicate that it's an identifier local to the function, while `fac` is prefixed with "@" to indicate that it is in scope in the entire compilation unit.

Next, at (2) we have the first instruction of the body of `fac`, which performs a signed comparison of the argument %n and 0 and assigns the result to the temporary %1. The instruction at (3) is a "terminator", and marks the end of the current block. It will transfer control to either ret at (4) or rec at (5). The labels at (4) and (5) each indicate the beginning of a new block of instructions. Notice that the entry block starting at (2) is not labeled: in LLVM it is illegal to jump back to the entry block of a function body. Moving on, (6) performs a subtraction and names the result %2. The i64 annotation indicates that both operands are 64-bit integers. The function `fac` is called at (7), and the result named %3. Again, the i64 annotations indicate that the single argument and the returned value are 64-bit integers.

Finally, (8) returns from the function with the result named by %4, and (9) defines the main function of the program, which simply calls fac with a literal i64 argument.

### §5.2 Introduction of Visitor

![ir_ast_preview](readme.assets/ir_ast_preview.svg)

To generate the IR mentioned above, we use a visitor class named `NanoVisitor`. Given an abstract syntax tree like the above figure, the visitor will first visit the `ProgNode` which is marked as root. Then the visitor will well grounded travel the children of root.

#### Design Pattern: Reflection

One problem in traveling step is that visitor does not know the type of node and thus can not do specific actions depending on the type of node. To solve this problem, we use the design pattern of reflection. That is, the visitor will call the `accept` method of class node. The derived classes of `Node` will override the `accept` method to their own visiting procedure. So, the calling flow is just like `Visitor->Node->Visitor` which can be interpreted as reflection. A piece of sample code is shown as below:

```python
class NanoVisitor(Visitor):
    # ...
    def visitProgNode(self, node: ProgNode):
        # ...
        for func in node.funcs:
            func.accept(self)
        # ...
```

```python
class ProgNode(Node):
    # ...
    def accept(self, visitor: NanoVisitor):
        return visitor.visitProgNode(self)
class FuncNode(Node):
    # ...
    def accept(self, visitor: NanoVisitor):
        return visitor.visitFuncNode(self)
# ...
```

### §5.4 Attributes

During the IR generation, or in the other words, travelly visiting the AST, we need to set some attributes which may be referenced afterwards. Several key attributes in the visitor are shown as below:

- cur_module: a `llvmlite.ir.Module` object. This obj provides the IR generation environment, we can do nothing without it.

- cur_func_name: a `str` object. Mark which function is currently processed, initialized with empty string.

- builder_stack: a `llvmlite.ir.IRBuilder` object. This obj is used to insert IR instructions after the blocks.

- scope_stack: a `list` object. Each element in the stack is of type `dict`. This obj denotes the symbol table and scopes. The procedure of getting an identifier in the current scope just work like below:

  ```python
      def _get_identifier(self, name):
          for d in self.scope_stack[::-1]:  # reversing the scope_block
              if name in d:
                  return d[name]['ref']
          return None
  ```

- loop_exit_stack & loop_entr_stack: a `list` object. Since we support nested loop statements, continue and break statements, we need to remember the last entrance/exit point(usually interpreted as the beginning of a block). The next time we analysis break or continue, we can pop the exit stack or entrance stack and branch there.

- in_global: a `bool` object. Mark whether the visitor is currently at the global scope. If it is, the declared variable will be allocated in the global space.

```python
class NanoVisitor(Visitor):
    def __init__(self):
        # we do not need list since we only support single filre compiling
        self.cur_module = None
        # we do not need list since we do not support sub-procedure
        self.cur_func_name = ''
        self.builder_stack = []
        self.block_stack = []
        self.scope_stack = []
        self.loop_exit_stack = []
        self.loop_entr_stack = []
        self.in_global = True
        # ...
```

### §5.3 Implementation of Visitor

We select several visiting examples to illustrate how visiting procedure generates IR.

#### VisitBlockNode

The special point of the BlockNode is that, we need to create a new scope every time we enter the block.

```python
    def visitBlockNode(self, node: BlockNode, scope=None):
        self._push_scope(scope)
        for stmt in node.stmts:
            stmt.accept(self)
        return self._pop_scope()
```

for every statements in this block, it will call accept method and generates their own part IR.

#### VisitIfStmtNode

For the IfStmtNode, we will first evaluate the condition:

```python
    def visitIfStmtNode(self, node: IfStmtNode):
		node.cond.accept(self)
        pred = self._get_builder().icmp_signed('!=',
                                               val(node.cond),
                                               ir.Constant(int32, 0))
        if type(node.ifbody) == EmptyStmtNode:
            return
    	#...
```

And then generate IR in `then` and `otherwise` part:

```python
    	if type(node.elsebody) == EmptyStmtNode:
            with self._get_builder().if_then(pred) as then:
                self._push_scope()
                node.ifbody.accept(self)
                self._pop_scope()
        else:
            with self._get_builder().if_else(pred) as (then, othrewise):
                with then:
                    # ifbody
                    self._push_scope()
                    node.ifbody.accept(self)
                    self._pop_scope()
                with othrewise:
                    # elsebody
                    self._push_scope()
                    node.elsebody.accept(self)
                    self._pop_scope()
```

Notice that we use the APIs of llvmlite which are `IRBuilder.if_then` and `IRBuilder.if_else`. The former will yield a basic block, and we can generate `then` part IR in this block. The latter will yield two context managers, we can use keyword `with` to set at the begining of that block and generate `then/otherwise` part IR in them. The generating IR work is recursively done in the accept calling.

#### VisitLoopNode

We support three loop statements: `for`, `while` and `do-while`. Their procedure of generating IR are somewhat different. This is because the difference of their loop structures which are illustrated as below:

```txt
for:
	pre: EmptyStmtNode / DecNode
	cond: EmptyExpNode / subclass of EmptyExpNode / subclass of EmptyLiteralNode / IDNode
	body: BlockNode
	post: EmptyExpNode / subclass of EmptyExpNode / subclass of EmptyLiteralNode / IDNode
while:
	pre: EmptyStmtNode
	cond: EmptyExpNode / subclass of EmptyExpNode / subclass of EmptyLiteralNode / IDNode
	body: BlockNode
	post: EmptyStmtNode
do-while:
	pre: EmptyStmtNode()
	cond: EmptyExpNode / subclass of EmptyExpNode / subclass of EmptyLiteralNode / IDNode
	body: BlockNode()
	post: EmptyStmtNode()
```

Based on above analysis, we divide the loop statements into two cases:

- `for` and `while`:

  ```python
              """ do-while
                  ...
                  branch body_block
              body_block:
                  body...
                  branch cond_block
              cond_block [continue target]:
                  cond...
                  branch(cond, body_block, tail_block)
              tail_block [break target]:
                  ...
              """
  ```

- `do-while`:

  ```python
              """ for & while
                  ...
                  pre...
                  branch cond_block
              cond_block:
                  cond...
                  branch(cond, body_block, tail_block)
              body_block:
                  body...
                  branch post_block
              post_block [continue target]:
                  post...
                  branch cond_block
              tail_block [break target]:
                  ...
              """
  ```

In addition, to support the declaration in the for statements like `for(int i=0;i<n;i++)`, we adopt the scope creating/deleting procedure like this:

```txt
                ...scope_original...
        /======================scope_new_0===/
        /  pre -> cond <----|                /
        /  /=========|======|==scope_new_1===/
        /  /        body    |                /
        /  /=========|======|================/
        /           post----|                /
        /====================================/
```

We show the for/while IR generation below, for more details pleased refer to our source code.

```python
            cond_block = self._get_builder().append_basic_block()
            body_block = self._get_builder().append_basic_block()
            post_block = self._get_builder().append_basic_block()
            tail_block = self._get_builder().append_basic_block()
            self.loop_entr_stack.append(post_block)
            self.loop_exit_stack.append(tail_block)

            # scope_new_0
            self._push_scope()
            if type(node.pre) != EmptyStmtNode:
                node.pre.accept(self)
            self._get_builder().branch(cond_block)

            # entrance
            self._get_builder().position_at_start(cond_block)
            if type(node.cond) != EmptyExpNode:
                node.cond.accept(self)
                cond = self._get_builder().icmp_signed('!=',
                                                       val(node.cond),
                                                       ir.Constant(int32, 0))
            else:
                cond = int1(1)
            self._get_builder().cbranch(cond, body_block, tail_block)

            # scope_new_1 auto created when visitBlockNode
            self._get_builder().position_at_start(body_block)
            node.body.accept(self)
            self._get_builder().branch(post_block)

            # return to scope 0
            self._get_builder().position_at_start(post_block)
            if type(node.post) != EmptyStmtNode:
                node.post.accept(self)
            self._get_builder().branch(cond_block)
            self._pop_scope()

            # after
            self._get_builder().position_at_start(tail_block)

            self.loop_entr_stack.pop()
            self.loop_exit_stack.pop()
```

#### VisitBinopNode

The generation of binary operation IR is very simple, it only calls some APIs of llvmlite. The used APIs are: `llvm.ir.IRBuilder.add`, `llvm.ir.IRBuilder.sub`, `llvm.ir.IRBuilder.mul`, `llvm.ir.IRBuilder.sdiv`, `llvm.ir.IRBuilder.srem`, `llvm.ir.IRBuilder.shl`, `llvm.ir.IRBuilder.ashr`, `llvm.ir.IRBuilder.icmp_signed`, `llvm.ir.IRBuilder.fadd`, `llvm.ir.IRBuilder.fsub`, `llvm.ir.IRBuilder.fmul`, `llvm.ir.IRBuilder.fdiv`, `llvm.ir.IRBuilder.frem`, `llvm.ir.IRBuilder.fcmp_ordered`, etc.

For example, the addition IR of two floating point number is generated by:

```python
            if node.op == '+':
                node.value = self._get_builder().fadd(
                    val(node.left),
                    val(node.right))
```

where the fadd method will automatically write an IR correspoing to floating point number addition into the whole IR module.

#### VisitUnaryNode

The unary operations are quite like binary operations. However, the differences are that some of unary operations like `*` and `&` are related to addressed and pointers which make them more complicated. For example, if we do `UnaryNode(*, IDNode(a))`, we need to first guarantee identifier is previously decalared and is a pointer type; Then we get the reference of a which is `ref(a):=&a` and then load the value which is `val(a):=load(ref(a))` and finally do the start operation `ref(*a):=val(a)`. The next time we need to load the value, we just `val(*a)=load(ref(*a))` and in the other case, store the value into `*a`, we use `store(value, ref(*a))`.

Some code is shown as below:

```python
        #...
    	elif node.op == '*':
            node.ref = val(node.node)
        elif node.op == '&':
            node.value = ref(node.node)
        #...
```

#### VisitArrSubNode

Since we support array type, we need to support getting value by indices like `arr[i][j][k]`. In LLVM IR, reference of `arr` is stored as pointer to its memory, and the type is `[i x [j x [k x int32]]]*`. In our AST, this expression is interpreted as `ArrSubNode(ArrSubNode(ArrSubNode(IDNode(arr), IDNode(i)), IDNode(j)), IDNode(k))`. So we can iteratively get the pointer use `llvmlite.ir.IRBuilder.gep`:

```python
    def visitArrSubNode(self, node: ArrSubNode):
        node.subee.accept(self)
        node.suber.accept(self)
        node.ref = self._get_builder().gep(ref(node.subee),
                                           [ir.Constant(int32, 0),
                                            val(node.suber), ])
        node.exp_type = str(node.ref.type.pointee)
```

Notice that every time we do indexing, we need to pass one extral 0 value. This is because when the gep method is returned, the return value will be wrapped by as pointer type. We need a 0 index to get rid of this wrapping.

## Chapter 6 - Compilation

![image-20210606212321294](readme.assets/image-20210606212321294.png)

This is an example of manually compiling the intermediate representation generated by our `nanoirgen.py`. You can always just use `python src/nanoirgen.py -g -i samples/quicksort.c -o results/irgen.ll -e .exe` to generate the output directly

### §6.1 IR to Assembly

This process can be executed by a the LLVM static compiler `llc` or just `clang`

If using clang, we should use `clang irgen.ll -S -o irgen.s` to produce the assembly for viewing

```shell
clang <input_llvm_ir_file> -S -o <output_asm_file>
```

In our implementation, we used the `os` package to call a system program and generate the result for us
shell:

python:

```python
os.system(' '.join(["clang", args.output, "-S", "-o", ass]))
```

![image-20210606212532064](readme.assets/image-20210606212532064.png)

File content of `irgen.s`

(Target Assembly Code)

![image-20210606212615383](readme.assets/image-20210606212615383.png)

### §6.2 Assembling the Executable

With the assembly, we can simple use a compiler like `gcc` or `clang` to produce the final executable machine code

```shell
clang <input_asm_file> -o <output_exec_file>
```

This can be done with `clang irgen.s -o irgen`

or `gcc irgen.s -o irgen`

In our implementation, we used the `os` package to call a system program and generate the result for us
shell:

python:

```python
os.system(' '.join(["clang", ass, "-o", exe]))
```

## Chapter 7 - Test Cases

### §7.1 Lexer

As the token list is defined in the [Token Definition](#§1.2 Token Definition) section, we wrote a file including all possible tokens (which is listed below) to test our lexer (`src/nanolex.py`). To run the lexer, use the command:

```bash
$ python3 src/nanolex.py samples/LexTest.txt
```

- **Input:** The file to be tokenized.
- **Output:** Tokens (in the format of `LexToken(<type>,<value>,<lineno>,<lexpos>)`).

Test cases:

1. **Keywords**

   Input:

   ```
   int float char void
   if else
   else if
   do while
   for
   continue break
   return
   ```

   Output:

   <img src="readme.assets/test/lex-1.png" alt="lex-1" style="zoom:80%;" />

2. **Identifiers**

   Input:

   ```
   thisIsAnIdentifier
   these are four Identifiers
   ```

   Output:

   <img src="readme.assets/test/lex-2.png" alt="lex-2" style="zoom:80%;" />

3. **Constants**

   Input:

   ```
   999 -233
   0.618 -6.666666
   ```

   Output:

   <img src="readme.assets/test/lex-3.png" alt="lex-3" style="zoom:80%;" />

4. **Operators**

   Input:

   ```
   + - * / %
   | & ~ ^ << >>
   || && !
   < <= > >= == !=
   ```

   Output:

   <img src="readme.assets/test/lex-4.png" alt="lex-4" style="zoom:80%;" />

5. **Assignments**

   Input:

   ```
   =
   *= /= %=
   += -=
   <<= >>= &= ^= |=
   ```

   Output:

   <img src="readme.assets/test/lex-5.png" alt="lex-5" style="zoom:80%;" />

6. **Increment & Decrement**

   Input:

   ```
   ++ --
   ```

   Output:

   <img src="readme.assets/test/lex-6.png" alt="lex-6" style="zoom:80%;" />

7. **Conditional Operator & Delimeters**

   Input:

   ```
   // Conditional Operator
   ?
   
   // Delimeters
   ( )
   [ ]
   { }
   . ,
   ; :
   ```

   Output:

   <img src="readme.assets/test/lex-7.png" alt="lex-7" style="zoom:80%;" />

In conclusion, the program `nanolex.py` tokenized the input files as desired in all the test cases. Test passed.

### §7.2 Yacc

The grammar productions used in Nano C is listed in [BNF Definition for the Nano C Language](#§2.2 BNF Definition for the Nano C Language). File `samples/ParserTest.c` contains **all grammar elements** which Nano C supports and is designed to test the parser implemented by yacc. To test the parser, simply use the command below:

```bash
$ python3 src/nanoyacc.py -i samples/ParserTest.c
```

The invocation of `nanoyacc.py` supports *command line options*. To learn how to use the options, you may do:

```bash
$ python3 src/nanoyacc.py -h
```

- **Input:** The file to be parsed.
- **Output:** 
  1. Abstract syntax tree (AST)
  2. Structed AST
  3. Visualized AST

The testing file (`samples/ParserTest.c`) is as the following. And the purposes of each statement / expression is commented right above them.

```c
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
```

Output after parsing the testing file:

1. CLI-printed **Abstract Syntax Tree (AST)** (partial)

   <img src="readme.assets/test/yacc-1.png" alt="yacc-1" style="zoom: 67%;" />

2. **Structed AST**

   ```
   {'name': 'Prog', '_children': [{'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{a}'}, {'name': 'Int{0}'}]}, {'name': 'Dec', '_children': [{'name': 'Type{long}'}, {'name': 'ID{l}'}, {'name': 'Int{9999999}'}]}, {'name': 'Dec', '_children': [{'name': 'Type{double}'}, {'name': 'ID{pi}'}, {'name': 'Float{3.141592}'}]}, {'name': 'Dec', '_children': [{'name': 'Type{float}'}, {'name': 'ID{f}'}, {'name': 'Float{0.03}'}]}, {'name': 'Dec', '_children': [{'name': 'Type{char}'}, {'name': 'ID{ch}'}, {'name': 'Char{a}'}]}, {'name': 'Dec', '_children': [{'name': 'Type{char}'}, {'name': 'ID{b}'}, {'name': 'Char{1}'}]}, {'name': 'Dec', '_children': [{'name': 'Type{char}'}, {'name': 'ID{e}'}, {'name': 'None'}]}, {'name': 'Dec', '_children': [{'name': 'Type{Type{char}}'}, {'name': 'ID{str}'}, {'name': 'None'}]}, {'name': 'Dec', '_children': [{'name': 'Type{char}'}, {'name': 'ID{thisIsAnArray}'}, {'name': '19'}, {'name': '20'}, {'name': '21'}, {'name': 'None'}]}, {'name': 'Func', '_children': [{'name': 'Type{int}'}, {'name': 'ID{main}'}, {'name': 'Block', '_children': [{'name': 'Dec', '_children': [{'name': 'Type{double}'}, {'name': 'ID{pi2}'}, {'name': 'Binary{*}', '_children': [{'name': 'ID{pi}'}, {'name': 'Int{2}'}]}]}, {'name': 'Dec', '_children': [{'name': 'Type{double}'}, {'name': 'ID{da}'}, {'name': '10'}, {'name': 'None'}]}, {'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{i}'}, {'name': 'None'}]}, {'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{j}'}, {'name': 'None'}]}, {'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{t}'}, {'name': 'None'}]}, {'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{controller}'}, {'name': 'Int{1}'}]}, {'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{condition}'}, {'name': 'Int{0}'}]}, {'name': 'Loop', '_children': [{'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{i}'}, {'name': 'Int{0}'}]}, {'name': 'Binary{<}', '_children': [{'name': 'ID{i}'}, {'name': 'Int{10}'}]}, {'name': 'Block{Ass{=}}', '_children': [{'name': 'ArrSub', '_children': [{'name': 'ID{da}'}, {'name': 'ID{i}'}]}, {'name': 'Binary{*}', '_children': [{'name': 'ID{i}'}, {'name': 'ID{pi}'}]}]}, {'name': 'Ass{=}', '_children': [{'name': 'ID{i}'}, {'name': 'Binary{+}', '_children': [{'name': 'ID{i}'}, {'name': 'Int{1}'}]}]}]}, {'name': 'Loop', '_children': [{'name': 'EmptyStmt'}, {'name': 'Int{1}'}, {'name': 'Block{EmptyStmt}'}, {'name': 'EmptyStmt'}]}, {'name': 'Loop', '_children': [{'name': 'Block{EmptyStmt}'}, {'name': 'while'}, {'name': 'Int{0}'}, {'name': 'EmptyStmt'}]}, {'name': 'Loop', '_children': [{'name': 'EmptyExp'}, {'name': 'EmptyExp'}, {'name': 'Block{EmptyStmt}'}, {'name': 'EmptyExp'}]}, {'name': 'Loop', '_children': [{'name': 'EmptyStmt'}, {'name': 'Int{1}'}, {'name': 'Block{Loop}', '_children': [{'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{n}'}, {'name': 'Int{100}'}]}, {'name': 'Binary{>=}', '_children': [{'name': 'ID{n}'}, {'name': 'Int{0}'}]}, {'name': 'Block{Loop}', '_children': [{'name': 'EmptyStmt'}, {'name': 'ID{controller}'}, {'name': 'Block{Loop}', '_children': [{'name': 'Block{Ass{=}}', '_children': [{'name': 'ID{str}'}, {'name': 'String{inside while loop}'}]}, {'name': 'while'}, {'name': 'Binary{==}', '_children': [{'name': 'ID{condition}'}, {'name': 'String{OK}'}]}, {'name': 'EmptyStmt'}]}, {'name': 'EmptyStmt'}]}, {'name': 'Ass{=}', '_children': [{'name': 'ID{n}'}, {'name': 'Binary{-}', '_children': [{'name': 'ID{n}'}, {'name': 'Int{1}'}]}]}]}, {'name': 'EmptyStmt'}]}, {'name': 'Loop', '_children': [{'name': 'Ass{=}', '_children': [{'name': 'ID{j}'}, {'name': 'Int{0}'}]}, {'name': 'Binary{<}', '_children': [{'name': 'ID{j}'}, {'name': 'Int{10}'}]}, {'name': 'Block{IfStmt}', '_children': [{'name': 'Binary{<}', '_children': [{'name': 'ArrSub', '_children': [{'name': 'ID{da}'}, {'name': 'ID{j}'}]}, {'name': 'Int{10}'}]}, {'name': 'Block{Continue}'}, {'name': 'Block', '_children': [{'name': 'Call', '_children': [{'name': 'ID{PrintHello}'}]}, {'name': 'Break'}]}]}, {'name': 'Ass{=}', '_children': [{'name': 'ID{j}'}, {'name': 'Binary{+}', '_children': [{'name': 'ID{j}'}, {'name': 'Int{1}'}]}]}]}, {'name': 'IfStmt', '_children': [{'name': 'Int{1}'}, {'name': 'Block{IfStmt}', '_children': [{'name': 'Int{2}'}, {'name': 'Block{Ass{=}}', '_children': [{'name': 'ID{l}'}, {'name': 'Int{222}'}]}, {'name': 'Block{Ass{=}}', '_children': [{'name': 'ID{l}'}, {'name': 'Int{223}'}]}]}, {'name': 'Block{IfStmt}', '_children': [{'name': 'Int{3}'}, {'name': 'Block{Ass{=}}', '_children': [{'name': 'ID{l}'}, {'name': 'Int{333}'}]}, {'name': 'Block{Ass{=}}', '_children': [{'name': 'ID{l}'}, {'name': 'Int{444}'}]}]}]}, {'name': 'Block', '_children': [{'name': 'Dec', '_children': [{'name': 'Type{double}'}, {'name': 'ID{t}'}, {'name': 'Float{6.06}'}]}, {'name': 'Block', '_children': [{'name': 'Dec', '_children': [{'name': 'Type{char}'}, {'name': 'ID{t}'}, {'name': 'Char{0}'}]}, {'name': 'Block', '_children': [{'name': 'Dec', '_children': [{'name': 'Type{int}'}, {'name': 'ID{t}'}, {'name': 'Int{0}'}]}, {'name': 'Ass{=}', '_children': [{'name': 'ID{t}'}, {'name': 'Binary{*}', '_children': [{'name': 'ID{pi}'}, {'name': 'ID{f}'}]}]}]}]}]}, {'name': 'EmptyStmt'}, {'name': 'EmptyStmt'}, {'name': 'EmptyStmt'}, {'name': 'EmptyStmt'}, {'name': 'EmptyStmt'}, {'name': 'EmptyStmt'}, {'name': 'Ass{=}', '_children': [{'name': 'ID{t}'}, {'name': 'Int{1}'}]}, {'name': 'Ass{=}', '_children': [{'name': 'ID{t}'}, {'name': 'Ass{=}', '_children': [{'name': 'ID{a}'}, {'name': 'Unary{-}{ID{j}}'}]}]}, {'name': 'Ternary', '_children': [{'name': 'Int{1}'}, {'name': '?'}, {'name': 'Int{2}'}, {'name': ':'}, {'name': 'Int{3}'}]}, {'name': 'Ternary', '_children': [{'name': 'ID{t}'}, {'name': '?'}, {'name': 'Ternary', '_children': [{'name': 'Int{1}'}, {'name': '?'}, {'name': 'Int{2}'}, {'name': ':'}, {'name': 'Int{3}'}]}, {'name': ':'}, {'name': 'Int{4}'}]}, {'name': 'Ternary', '_children': [{'name': 'Int{0}'}, {'name': '?'}, {'name': 'Int{2}'}, {'name': ':'}, {'name': 'Ternary', '_children': [{'name': 'Int{3}'}, {'name': '?'}, {'name': 'Ternary', '_children': [{'name': 'ID{t}'}, {'name': '?'}, {'name': 'Int{4}'}, {'name': ':'}, {'name': 'Int{5}'}]}, {'name': ':'}, {'name': 'Int{6}'}]}]}, {'name': 'Binary{||}', '_children': [{'name': 'Binary{&&}', '_children': [{'name': 'Int{1}'}, {'name': 'Int{2}'}]}, {'name': 'Binary{&&}', '_children': [{'name': 'Int{3}'}, {'name': 'Int{4}'}]}]}, {'name': 'Binary{||}', '_children': [{'name': 'Int{1}'}, {'name': 'Binary{&&}', '_children': [{'name': 'Binary{||}', '_children': [{'name': 'ID{t}'}, {'name': 'Int{3}'}]}, {'name': 'Int{4}'}]}]}, {'name': 'Binary{^}', '_children': [{'name': 'ID{e}'}, {'name': 'ID{e}'}]}, {'name': 'Binary{|}', '_children': [{'name': 'Binary{|}', '_children': [{'name': 'Binary{&}', '_children': [{'name': 'ID{t}'}, {'name': 'ID{e}'}]}, {'name': 'Binary{^}', '_children': [{'name': 'Int{3}'}, {'name': 'Int{5}'}]}]}, {'name': 'Binary{|}', '_children': [{'name': 'ID{j}'}, {'name': 'ID{e}'}]}]}, {'name': 'Binary{==}', '_children': [{'name': 'ID{t}'}, {'name': 'Int{1}'}]}, {'name': 'Binary{>=}', '_children': [{'name': 'ID{e}'}, {'name': 'Char{a}'}]}, {'name': 'Binary{!=}', '_children': [{'name': 'Binary{==}', '_children': [{'name': 'Int{1}'}, {'name': 'Binary{<}', '_children': [{'name': 'Int{2}'}, {'name': 'Int{3}'}]}]}, {'name': 'Binary{>=}', '_children': [{'name': 'Binary{>}', '_children': [{'name': 'Binary{<=}', '_children': [{'name': 'Int{4}'}, {'name': 'Int{5}'}]}, {'name': 'Int{6}'}]}, {'name': 'Int{7}'}]}]}, {'name': 'Binary{>>}', '_children': [{'name': 'ID{a}'}, {'name': 'Int{10}'}]}, {'name': 'Binary{<<}', '_children': [{'name': 'Binary{>>}', '_children': [{'name': 'Int{2}'}, {'name': 'Int{3}'}]}, {'name': 'Int{4}'}]}, {'name': 'Binary{+}', '_children': [{'name': 'ID{i}'}, {'name': 'Int{1}'}]}, {'name': 'Binary{+}', '_children': [{'name': 'Int{100}'}, {'name': 'Binary{/}', '_children': [{'name': 'Int{30}'}, {'name': 'Float{4.0}'}]}]}, {'name': 'Unary{~}{ID{a}}'}, {'name': 'Unary{-}{Int{100}}'}, {'name': 'Unary{Type{int}}{Unary{!}{Binary{+}}}', '_children': [{'name': 'Unary{*}{Binary{+}}', '_children': [{'name': 'Binary{+}', '_children': [{'name': 'Unary{&}{ID{t}}'}, {'name': 'Unary{+}{Int{1}}'}]}, {'name': 'Unary{-}{Int{1}}'}]}, {'name': 'Unary{*}{Ass{=}}', '_children': [{'name': 'ID{str}'}, {'name': 'Binary{+}', '_children': [{'name': 'ID{str}'}, {'name': 'Int{1}'}]}]}]}, {'name': 'Binary{||}', '_children': [{'name': 'Int{1}'}, {'name': 'Binary{&&}', '_children': [{'name': 'Int{0}'}, {'name': 'Binary{==}', '_children': [{'name': 'Int{4}'}, {'name': 'Binary{>=}', '_children': [{'name': 'Int{3}'}, {'name': 'Binary{-}', '_children': [{'name': 'Int{2}'}, {'name': 'Binary{*}', '_children': [{'name': 'Int{1}'}, {'name': 'Unary{-}{Int{1}}'}]}]}]}]}]}]}, {'name': 'Ass{=}', '_children': [{'name': 'ID{e}'}, {'name': 'Ternary', '_children': [{'name': 'Binary{<}', '_children': [{'name': 'ID{i}'}, {'name': 'ID{t}'}]}, {'name': '?'}, {'name': 'Ass{=}', '_children': [{'name': 'ID{a}'}, {'name': 'Binary{+}', '_children': [{'name': 'ID{a}'}, {'name': 'Int{1}'}]}]}, {'name': ':'}, {'name': 'Binary{&&}', '_children': [{'name': 'ID{a}'}, {'name': 'ID{t}'}]}]}]}, {'name': 'Ass{=}', '_children': [{'name': 'ArrSub', '_children': [{'name': 'ID{da}'}, {'name': 'Int{2}'}]}, {'name': 'Binary{+}', '_children': [{'name': 'ArrSub', '_children': [{'name': 'ID{da}'}, {'name': 'Int{2}'}]}, {'name': 'Int{1}'}]}]}, {'name': 'Ret{Int{0}}'}]}]}, {'name': 'Func', '_children': [{'name': 'Type{void}'}, {'name': 'ID{PrintHello}'}, {'name': 'Block', '_children': [{'name': 'Call', '_children': [{'name': 'ID{printf}'}, {'name': 'String{Hello, Nano C!}'}]}, {'name': 'Ret{EmptyExp}'}]}]}, {'name': 'Func', '_children': [{'name': 'Type{int}'}, {'name': 'ID{max}'}, {'name': 'Param', '_children': [{'name': 'Type{int}'}, {'name': 'ID{a}'}]}, {'name': 'Param', '_children': [{'name': 'Type{int}'}, {'name': 'ID{b}'}]}, {'name': 'Block{Ret{Ternary}}', '_children': [{'name': 'Binary{>}', '_children': [{'name': 'ID{a}'}, {'name': 'ID{b}'}]}, {'name': '?'}, {'name': 'ID{a}'}, {'name': ':'}, {'name': 'ID{b}'}]}]}], 'size': [2111.1111111111113, 911.1111111111111], 'filename': 'samples/ParserTest.c'}
   ```

   This structed tree is in `json` format and is sent to our server to create a visualized and interactive AST on the webpage.

3. **Visualized AST** (partial)

   The visualized AST is too long to be screenshotted in a single page. You may see the complete version of the fancy-visualized AST in [Introduction of Visitor](#§5.2 Introduction of Visitor).

   <img src="readme.assets/test/yacc-2.png" alt="yacc-2" style="zoom: 67%;" />

Obtaining the above results with enough complexity, we carefully examined each one of the output. It turned out that **all nodes were parsed as desired**, with satisfying orders and precedence. **We can conclude that our parser passed the test.**

### §7.3 IR Generation and Execution

**Checkpoint** 1

```c
/**
 * checkpoint 1
 * feature:
 *      single function & directly return
 * expected output: 0
 */
int main() {
    return 0;
}
```

![image-20210606214039710](./readme.assets/image-20210606214039710.png)

**Checkpoint** 2

```c
/**
 * checkpoint 2
 * feature:
 *      single function
 *      single type variable declarations
 * expected output: 0
 */
int main() {
    int a;
    int b;
    int c;
    return 0;
}
```

![image-20210606214029210](./readme.assets/image-20210606214029210.png)

**Checkpoint** 3

```c
/**
 * checkpoint 3
 * feature:
 *      single function
 *      initilizers & declaration list
 *      assignment expressions
 * expected output: 6
 */
int main() {
    int a = 0, b = 1, c = 2, d = 3;
    a = b*c*d;
    return a;
}
```

![image-20210606214018531](./readme.assets/image-20210606214018531.png)

**Checkpoint** 4

```c
/**
 * checkpoint 4
 * feature:
 *      single function
 *      initilizers & declaration list
 *      assignment expressions
 *      more complicated expression
 *      implicit type casting from int1 to int32
 * expected output: 3
 */
int main() {
    int a = 0, b = 1, c = 2, d = 3;
    a = ((b*c*d) && (a*d)) + (((c+b)/d) || a) + b*c;
    return a;
}
```

![image-20210606214006372](./readme.assets/image-20210606214006372.png)

**Checkpoint** 5

```c
/**
 * checkpoint 5
 * feature:
 *      integer type
 *      multiple functions & function call
 * expected output: 2
 */
int two() { return 2; }
int main() {
    return two();
}
```

![image-20210606213956059](./readme.assets/image-20210606213956059.png)

**Checkpoint** 6

```c
/**
 * checkpoint 6
 * feature:
 *      integer type
 *      multiple functions & function call
 *      if-else statements
 *      loop statements
 * expected output: 20
 */
int sum_up_to(int a) {
    int sum = 0;
    for (int i=0;i<a;i=i+1)
        sum = sum + i;
    return sum;
}
int main() {
    int a = 5;
    if (a % 2) return 2*sum_up_to(a);
    else return sum_up_to(a);
}
```

![image-20210606213945661](./readme.assets/image-20210606213945661.png)

**Checkpoint** 7

```c
/**
 * checkpoint 7
 * feature:
 *      integer type
 *      multiple functions & function call
 *      nested if-else statements
 *      recursion functions
 * expected output: 8
 */
int fib(int n) {
    if (n <= 0) return 0;
    else if (n == 1) return 1;
    else if (n == 2) return 1;
    else return fib(n - 1) + fib(n - 2);
}
int main() {
    int a = 6;
    return fib(a);
}
```

![image-20210606213930583](./readme.assets/image-20210606213930583.png)

**Checkpoint** 8

```c
/**
 * checkpoint 8
 * feature:
 *      integer type
 *      multiple functions & function call
 *      nested if-else statements
 *      recursion functions
 *      nested loop statements
 *      break & continue
 * expected output: 595
 */
int fib(int n) {
    // 1 1 2 3 5 8 13 21 34
    if (n <= 0) return 0;
    else if (n == 1) return 1;
    else if (n == 2) return 1;
    else return fib(n - 1) + fib(n - 2);
}
int main() {
    int sum = 0;
    for (int a = 4; a < 10; a++) {
        if (a == 6) continue;
        else if (fib(a) % 2 == 0) {
            for (int b = fib(a); b > 0; b=b-1)
                sum = sum + b;
            break;
        }
    }
    return sum;
}
```

![image-20210606213902148](./readme.assets/image-20210606213902148.png)

**Checkpoint** 9

```c
/**
 * checkpoint 9
 * feature:
 *      void return type
 *      integer type & pointer type
 *      & and * operator
 *      value swap with pointers
 * expected output: 2
 */
void swap(int *a, int *b) {
    int c = *a;
    *a = *b;
    *b = c;
}
int main() {
    int a=1, b=2;
    int *c = &a;
    int *d = &b;
    swap(c,d);
    return a;
}
```

![image-20210606213817850](./readme.assets/image-20210606213817850.png)

**Checkpoint** 10

```c
/**
 * checkpoint 10
 * feature:
 *      integer type & pointer type
 *      array type
 *      & and * operator
 *      value swap with pointers
 * expected output: 7
 */
void swap(int* a, int* b) {
    int c = *a;
    *a = *b;
    *b = c;
}
int main() {
    int a[3][3];
    a[0][0] = 0; a[0][1] = 1; a[0][2] = 2;
    a[1][0] = 3; a[1][1] = 4; a[1][2] = 5;
    a[2][0] = 6; a[2][1] = 7; a[2][2] = 8;
    int b=1, c=2;
    int *ptr_to_b = &b;
    int *ptr_to_c = &c;
    swap(ptr_to_b,ptr_to_c);
    return a[b][c];
}
```

![image-20210606213801033](./readme.assets/image-20210606213801033.png)

**Checkpoint** 11

```c
/**
 * checkpoint 11
 * feature:
 *      integer type & float type & void type
 *      pointer type & array type
 *      & and * operator
 *      type casting:
 *          xd array -> pointer
 *          int <-> float
 *      gloabl variables
 *      multi-scopes
 *      calculations:
 *          *(pointer + integer)
 * expected output: 12
 */

int n = 10;
int a[10][10];

int main() {
    int i = 3, j = 3;
    for (int i=0; i<n;i=i+1) {
        for (int j=0; j<n; j=j+1) {
            a[i][j] = i+j;
        }
    }
    int * arr_ptr = (int*)a;
    *(arr_ptr + i*n + j) = 2 * *(arr_ptr + i*n + j);
    return a[i][j];
}
```

![image-20210606213745784](./readme.assets/image-20210606213745784.png)

**Checkpoint** 12

```c
/**
 * checkpoint 12
 * feature:
 *      integer type & float type & void type
 *      pointer type & array type
 *      & and * operator
 *      type casting:
 *          xd array -> pointer
 *          int <-> float
 *      calculations:
 *          *(pointer + integer)
 *      quicksort
 *      random integer generation
 * expected output: 1
 */

int qsort(int * a, int l, int r)
{
    int i = l;
    int j = r;
    int p = *(a + ((l + r)/2));
    int flag = 1;
    while (i <= j) {
        while (*(a+i) < p) i = i + 1;
        while (*(a+j) > p) j = j - 1;
        if (i > j) break;
        int u = *(a+i);
        *(a+i) = *(a+j);
        *(a+j) = u;
        i = i + 1;
        j = j - 1;
    }
    if (i < r) qsort(a, i, r);
    if (j > l) qsort(a, l, j);
    return 0;
}

// random floating point number distributed uniformly in [0,1]
float rand(float *r) {
    float base=256.0;
    float a=17.0;
    float b=139.0;
    float temp1=a*(*r)+b;
    float temp2=(float)(int)(temp1/base);
    float temp3=temp1-temp2*base;
    *r=temp3;
    float p=*r/base;
    return p;
}

int initArr(int* a, int n)
{
    float state = 114514.0;
    int i =0;
    while (i < n) {
        *(a + i) = (int)(255*rand(&state));
        i = i + 1;
    }
}

int isSorted(int *a, int n)
{
    int i = 0;
    while (i < n - 1) {
        if ( (*(a+i)) > (*(a+i+1)))
            return 0;
        i = i + 1;
    }
    return 1;
}

int main()
{
    int n = 100;
    int arr[100];
    int * a = (int*)arr;
    initArr(a, n);
    qsort(a, 0, n - 1);
    return isSorted(a, n);
}
```

![image-20210606213723061](./readme.assets/image-20210606213723061.png)

**Checkpoint** 13

```c
/**
 * checkpoint 13
 * feature:
 *      integer type & float type & void type
 *      pointer type & array type
 *      & and * operator
 *      type casting:
 *          xd array -> pointer
 *          int <-> float
 *      calculations:
 *          *(pointer + integer)
 *      multiplication of matrix
 * expected output: 0
 */

int mulMatrix(int n, int *a, int *b, int *c) {
    int i; int j; int k;
    i = 0;
    while (i < n) {
        j = 0;
        while (j < n) {
            *(c + i*n + j) = 0;
            k = 0;
            while (k < n) {
                int old = *(c + i*n + j);
                *(c + i*n + j) = old + *(a+i*n + k) * (*(b+k*n + j));
                k = k + 1;
            }
            j = j + 1;
        }
        i = i + 1;
    }
}

int initMatrix(int n, int *a) {
int i; int j; int k;
    k = 0;
    i = 0;
    while (i < 2) {
        j = 0;
        while (j < 2) {
            k = k + 1;
            *(a + i*n + j) = k;
            j = j + 1;
        }
        i = i + 1;
    }
}

int a[2][2]; int b[2][2]; int c[2][2];
int main() {
    initMatrix(2, (int*)a);
    mulMatrix(2, (int*)a, (int*)a, (int*)b);
    mulMatrix(2, (int*)b, (int*)b, (int*)c);
    if (c[0][0] != 199)
        return 1;
    if (c[0][1] != 290)
        return 2;
    if (c[1][0] != 435)
        return 3;
    if (c[1][1] != 634)
        return 4;
    return 0;
}
```

![image-20210606213708636](./readme.assets/image-20210606213708636.png)

**Checkpoint** 14

```c

/**
 * checkpoint 13
 * feature:
 *      dijkstar shortest path algorithm
 * expected output: 17
 */

int main(void)
{
    int e[10][10], dis[10], book[10], i, j, m, n, t1, t2, t3, u, v, min;
    n = 6;
    m = 9;
    int inf = 99999;
    for (i = 1; i <= n; i++)
        for (j = 1; j <= n; j++)
            e[i][j] = inf;
    e[1][2] = 1;
    e[1][3] = 12;
    e[2][3] = 9;
    e[2][4] = 3;
    e[3][5] = 5;
    e[4][3] = 4;
    e[4][5] = 13;
    e[4][6] = 15;
    e[5][6] = 4;
    for (i = 1; i <= n; i++)
        dis[i] = e[1][i];  //初始化dis数组，表示1号顶点到其他顶点的距离
    for (i = 1; i <= n; i++)
        book[i] = 0;
    book[i] = 1;  //记录当前已知第一个顶点的最短路径
    for (i = 1; i <= n - 1; i++)
        for (i = 1; i <= n - 1; i++) {  //找到离一号顶点最近的点
            min = inf;
            for (j = 1; j <= n; j++) {
                if (book[j] == 0 && dis[j] < min) {
                    min = dis[j];
                    u = j;
                }
            }
            book[u] = 1;  //记录当前已知离第一个顶点最近的顶点
            for (v = 1; v <= n; v++) {
                if (e[u][v] < inf) {
                    if (dis[v] > dis[u] + e[u][v])
                        dis[v] = dis[u] + e[u][v];
                }
            }
        }
    //0 1 8 4 13 17
    return dis[6];
}
```

![image-20210606213651435](./readme.assets/image-20210606213651435.png)
