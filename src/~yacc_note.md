example:

```c
int main() { return 0; }
```

parsing:

```c
function_definition
    // {return 0;}
	=> declaration_specifiers id_declarator declaration_list_opt <compound_statement>
	=> *** brace_open block_item_list_opt brace_close
	=> *** brace_open block_item_list brace_close
	=> *** brace_open block_item brace_close
	=> *** brace_open statement brace_close
	=> *** brace_open jump_statement brace_close
	=> *** brace_open RETURN expression SEMI brace_close
	=> *** brace_open RETURN assignment_expression SEMI brace_close
	=> *** brace_open RETURN conditional_expression SEMI brace_close
	=> *** brace_open RETURN binary_expression SEMI brace_close
	=> *** brace_open RETURN cast_expression SEMI brace_close
	=> *** brace_open RETURN unary_expression SEMI brace_close
	=> *** brace_open RETURN postfix_expression SEMI brace_close
	=> *** brace_open RETURN primary_expression SEMI brace_close
	=> *** brace_open RETURN constant SEMI brace_close
	// int
    => <declaration_specifiers> id_declarator declaration_list_opt compound_statement
    => type_specifier ***
    => type_specifier_no_typeid ***
    => INT ***
    // main()
    => declaration_specifiers <id_declarator declaration_list_opt> compound_statement
    => *** id_declarator ***
    => *** direct_id_declarator ***
    => *** direct_id_declarator LPAREN parameter_type_list RPAREN ***
    => *** direct_id_declarator LPAREN parameter_list RPAREN ***
    => *** direct_id_declarator LPAREN RPAREN ***
    => *** ID LPAREN RPAREN ***
```



example:

```c
int sum(int a, int b) {
    int c = a + b;
    return c;
}
```

parsing:

```c
function_definition
    // {int c=a+b; return c;}
    => declaration_specifiers id_declarator declaration_list_opt <compound_statement>
	=> *** brace_open block_item_list_opt brace_close
	=> *** brace_open block_item_list brace_close
	=> *** brace_open block_item block_item_list brace_close
    // return c;
    => *** brace_open block_item <block_item> brace_close
    => *** statement ***
    => *** jump_statement ***
    => *** RETURN expression SEMI ***
    => ...
    => *** RETURN primary_expression SEMI ***
    => *** RETURN identifier SEMI ***
    // int c=a+b;
    => *** brace_open <block_item> block_item brace_close
    => *** declaration ***
    => *** decl_body SEMI ***
    => *** declaration_specifiers init_declarator_list_opt ***
    => *** type_specifier init_declarator_list ***
    => *** type_specifier init_declarator ***
    => *** type_specifier declarator EQUALS initializer ***
    => *** type_specifier id_declarator EQUALS initializer ***
    => *** type_specifier id_declarator EQUALS assignment_expression ***
```



example:

```c
int initMatrix(int n, int *a);
```

parsing:

```c
declaration
    // initMatrix(int n, int *a);
    => decl_body SEMI
    => declaration_specifiers init_declarator_list SEMI
    => type_specifiers init_declarator SEMI
    => type_specifiers declarator SEMI
    => type_specifiers <id_declarator> SEMI
    => *** direct_id_declarator LPAREN parameter_type_list RPAREN SEMI
    => *** direct_id_declarator LPAREN parameter_list RPAREN SEMI
    // int *a
    => direct_id_declarator LPAREN parameter_declaration COMMA <parameter_declaration> RPAREN SEMI
    => *** declaration_specifiers id_declarator ***
    => *** declaration_specifiers direct_id_declarator ***
    => *** declaration_specifiers pointer direct_id_declarator ***
    => ...
    => *** INT TIMES ID
```



example:

```c
int old = c[i*n + j];
```

parsing:
```c
// c[i*n + j]
initializer
    => assignment_expression
    => conditional_expression
    => binary_expression
    => cast_expression
    => unary_expression
    => postfix_expression LBRACKET expression RBRACKET
    => ...
```



example:

```c
c[i*n + j] = old + a[i*n + k] * b[k*n + j];
```

parsing:

```c
statement
    => expression_statement
    => expression SEMI
    => assignment_expression SEMI
    => unary_expression assignment_operator assignment_expression SEMI
```



example:

```c
int a[2][2]; 
```

parsing:

```c
declaration
    => decl_body SEMI
    => declaration_specifiers init_declarator_list SEMI
    => declaration_specifiers init_declarator SEMI
    // a[2][2]
    => declaration_specifiers <declarator> SEMI
    => *** id_declarator  ***
    => *** direct_id_declarator ***
    //[2]
    => *** direct_id_declarator LBRACKET assignment_expression_opt TIMES RBRACKET ***
    => *** direct_id_declarator LBRACKET assignment_expression_opt TIMES RBRACKET LBRACKET assignment_expression_opt TIMES RBRACKET ***
```



example:

```c
initMatrix(2, (int*)a);
```

parsing:

```c
postfix_expression
    => postfix_expression LPAREN argument_expression_list RPAREN
    => postfix_expression LPAREN argument_expression COMMA argument_expression RPAREN
    => ...
```



example:

```c
if (c[0][0] != 199)
	return 1;
```

parsing:

```c
statement
    => selection_statement
    => IF LPAREN expression RPAREN statement
    => ...
```



example:

```c
while (i < 2) {
    i = i + 1;
}
```

parsing:

```c
statement
    => iteration_statement
    => WHILE LPAREN expression RPAREN statement
    => ...
```



example:

```c
for (i=0; i<2; i++);
```

parsing:

```c
statement
    => iteration_statement
    => FOR LPAREN expression_opt SEMI expression_opt SEMI expression_opt RPAREN statement
    => ...
```

