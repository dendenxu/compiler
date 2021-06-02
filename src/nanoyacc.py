from ply import yacc
from nanolex import NanoLexer
from nanoast import *
import sys

class NanoParser():
    def __init__(self):
        self.parser = yacc.yacc(module=self)

    def p_binary_operators(self, p):
        '''expression : expression PLUS term
                    | expression MINUS term
           term       : term TIMES factor
                    | term DIVIDE factor'''
        p[0] = BinopNode(p[2], p[1], p[3])

    def p_expression_term(self, p):
        'expression : term'
        p[0] = p[1]

    def p_term_factor(self, p):
        'term : factor'
        p[0] = p[1]

    def p_factor_num(self, p):
        'factor : INT_CONST_DEC'
        p[0] = IntNode(int(p[1]))

    def p_factor_expr(self, p):
        'factor : LPAREN expression RPAREN'
        p[0] = p[2]

    # Error rule for syntax errors
    def p_error(self, p):
        print("Syntax error in input!")

    def parse(self, input, lexer=None) -> Node:
        return self.parser.parse(input, lexer)

    tokens = NanoLexer.tokens


if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        parser = NanoParser()
        visitor = NanoVisitor()
        root = parser.parse(content)
        print(f"Tree: {root}")
        result = root.accept(visitor)
        print(f"Result: {result}")
