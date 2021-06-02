from ply import yacc
from nanolex import NanoLexer
from nanoast import *
import sys
from termcolor import colored

"""
program    : function
function   : type ID LPAREN RPAREN LBRACE statement RBRACE
type       : INT
statement  : RETURN expression SEMI
expression : unary
unary      : INT_CONST_DEC
           | (MINUS|PLUS|NOT|LNOT) unary
"""


class NanoParser():
    def __init__(self):
        self.parser = yacc.yacc(module=self)

    def p_prog_func(self, p):
        'program    : function'
        p[0] = ProgNode(p[1])

    def p_func_def(self, p):
        'function   : type ID LPAREN RPAREN LBRACE statement RBRACE'
        p[0] = FuncNode(p[1], p[2], p[6])

    def p_type_def(self, p):
        'type       : INT'
        p[0] = TypeNode(p[1])

    def p_stmt_exp(self, p):
        'statement  : RETURN expression SEMI'
        p[0] = StmtNode(p[2])

    def p_exp_unary(self, p):
        'expression : unary'
        p[0] = ExpNode(p[1])

    def p_unary_int(self, p):
        'unary      : INT_CONST_DEC'
        p[1] = IntNode(int(p[1]))
        p[0] = UnaryNode('+', p[1])

    def p_unary_op(self, p):
        '''unary      : PLUS unary
                      | MINUS unary
                      | NOT unary
                      | LNOT unary
        '''
        p[0] = UnaryNode(p[1], p[2])

    # def p_binary_operators(self, p):
    #     '''expression : expression PLUS term
    #                 | expression MINUS term
    #        term       : term TIMES factor
    #                 | term DIVIDE factor'''
    #     p[0] = BinopNode(p[2], p[1], p[3])

    # def p_expression_term(self, p):
    #     'expression : term'
    #     p[0] = p[1]

    # def p_term_factor(self, p):
    #     'term : factor'
    #     p[0] = p[1]

    # def p_factor_num(self, p):
    #     'factor : INT_CONST_DEC'
    #     p[0] = IntNode(int(p[1]))

    # def p_factor_expr(self, p):
    #     'factor : LPAREN expression RPAREN'
    #     p[0] = p[2]

    # Error rule for syntax errors

    def p_error(self, p):
        print(colored("Error: ", "red")+"Syntax error when parsing "+str(p))

    def parse(self, input, lexer=None) -> Node:
        try:
            return self.parser.parse(input, lexer)
        except Exception as e:
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
