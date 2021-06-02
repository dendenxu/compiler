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
           | empty
type       : INT

statement  : RETURN expression SEMI
           | expression SEMI
           | declaration
           | SEMI

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

expression
    : logical_or

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

    def p_stmt_exp(self, p):
        'statement  : expression SEMI'
        p[0] = p[2]

    # def p_stmt_dec(self, p):
    #     'statement : declaration'
    #     p[0] = p[1]

    def p_stmt_semi(self, p):
        'statement : SEMI'
        pass

    def p_exp_lor(self, p):
        'expression : logical_or'
        p[0] = p[1]

    def p_lor_land(self, p):
        'logical_or : logical_and'
        p[0] = p[1]

    def p_land_eq(self, p):
        'logical_and : equality'
        p[0] = p[1]

    def p_add_mult(self, p):
        'additive : multiplicative'
        p[0] = p[1]

    def p_mult_unary(self, p):
        'multiplicative : unary'
        p[0] = p[1]

    def p_unary_prim(self, p):
        'unary : primary'
        p[0] = p[1]

    def p_prim_exp(self, p):
        'primary : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_primary_int(self, p):
        'primary      : INT_CONST_DEC'
        p[0] = IntNode(int(p[1]))

    def p_eq_relation(self, p):
        'equality    : relational'
        p[0] = p[1]

    def p_relation_add(self, p):
        'relational   : additive'
        p[0] = p[1]

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
