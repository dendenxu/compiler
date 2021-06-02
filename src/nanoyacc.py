from ply import yacc
from nanolex import NanoLexer
from nanoast import *
import sys
from termcolor import colored
import traceback

"""
program    : function
function   : type ID LPAREN RPAREN LBRACE block RBRACE
block      : block statement
           | 
type       : INT

statement  : RETURN expression SEMI
           | expression SEMI
           | declaration
           | SEMI

declaration
    : type ID typeinit_empty SEMI

typeinit_empty : typeinit
               | 

typeinit : EQUALS expression

expression
    : assignment

assignment
    : logical_or
    | ID EQUALS expression

additive
    : multiplicative
    | additive (PLUS|MINUS) multiplicative

multiplicative
    : unary
    | multiplicative (TIMES|DEVIDE|MOD) unary

unary
    : primary
    | (PLUS|MINUS|NOT|LNOT) unary

primary
    : INT_CONST_DEC
    | LPAREN expression RPAREN

equality
    : relational
    | equality (EQ|NE) relational

relational
    : additive
    | relational (LT|GT|LE|GE) additive

logical_or
    : logical_and
    | logical_or LOR logical_and

logical_and
    : equality
    | logical_and LAND equality
"""


class NanoParser():
    def __init__(self):
        self.parser = yacc.yacc(module=self)

    def p_prog_func(self, p):
        'program    : function'
        p[0] = ProgNode(p[1])

    def p_func_def(self, p):
        'function   : type ID LPAREN RPAREN LBRACE block RBRACE'
        p[0] = FuncNode(p[1], p[2], p[6])

    def p_type_def(self, p):
        'type       : INT'
        p[0] = TypeNode(p[1])

    def p_stmt_ret_exp(self, p):
        'statement  : RETURN expression SEMI'
        p[0] = RetNode(p[2])

    def p_pass_on_first(self, p):
        '''
        statement  : expression SEMI
        expression : assignment
        assignment : logical_or
        logical_or : logical_and
        logical_and : equality
        additive : multiplicative
        multiplicative : unary
        unary : primary
        equality    : relational
        relational   : additive
        statement : declaration
        typeinit_empty : typeinit
        '''
        p[0] = p[1]

    def p_pass_on_second(self, p):
        '''
        typeinit : EQUALS expression
        '''
        p[0] = p[2]

    def p_stmt_semi(self, p):
        'statement : SEMI'
        pass

    def p_declaration(self, p):
        '''
        declaration    : type ID typeinit_empty SEMI
        '''
        p[0] = DecNode(p[1], p[2], p[3])

    def p_assignment(self, p):
        '''
        assignment : ID EQUALS expression
        '''
        p[0] = AssNode(p[1], p[3])

    def p_prim_exp(self, p):
        'primary : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_primary_int(self, p):
        'primary      : INT_CONST_DEC'
        p[0] = IntNode(int(p[1]))

    def p_unary_op(self, p):
        '''unary      : PLUS unary
                      | MINUS unary
                      | NOT unary
                      | LNOT unary
        '''
        p[0] = UnaryNode(p[1], p[2])

    def p_binary_operators(self, p):
        '''additive       : additive PLUS multiplicative
                          | additive MINUS multiplicative
           multiplicative : multiplicative TIMES unary
                          | multiplicative DIVIDE unary
           equality       : equality EQ relational
                          | equality NE relational
           relational     : relational LT additive
                          | relational GT additive
                          | relational GE additive
                          | relational LE additive
           logical_or     : logical_or LOR logical_and
           logical_and    : logical_and LAND equality
        '''
        p[0] = BinopNode(p[2], p[1], p[3])

    def p_empty(self, p):
        '''
        block : 
        typeinit_empty :
        '''
        p[0] = None

    def p_block_stmt(self, p):
        '''
        block : block statement
        '''
        if p[1] is None:
            p[1] = BlockNode()
        p[1].append(p[2])
        p[0] = p[1]

    # Error rule for syntax errors

    def p_error(self, p):
        print(colored("Error: ", "red")+"Syntax error when parsing "+str(p))

    def parse(self, input, lexer=None) -> Node:
        try:
            return self.parser.parse(input, lexer)
        except Exception as e:
            traceback.print_exc()
            print(colored("Error: ", "red")+f"{e}")

    tokens = NanoLexer.tokens


if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        parser = NanoParser()
        # visitor = NanoVisitor()
        root = parser.parse(content)
        print(f"Tree: {root}")
        # result = root.accept(visitor)
        # print(f"Result: {result}")
