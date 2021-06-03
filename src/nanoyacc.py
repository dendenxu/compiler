from ply import yacc
from nanolex import NanoLexer
from nanoast import *
import sys
from termcolor import colored
import traceback

""" 
Productions used in the parser:

program             : function
function            : type ID LPAREN RPAREN curl_block
block               : block statement
                    | 
type                : INT
statement           : RETURN expression SEMI
                    | expression SEMI
                    | declaration
                    | SEMI
                    | IF LPAREN expression RPAREN ctrl_block ELSE ctrl_block
                    | IF LPAREN expression RPAREN ctrl_block
ctrl_block          : curl_block
                    | statement
curl_block          : LBRACE block RBRACE
declaration         : type declist SEMI
declist             : declist COMMA ID typeinit
                    | ID typeinit
typeinit            : EQUALS expression
                    | 
expression          : assignment
assignment          : conditional
                    | ID EQUALS expression
conditional         : logical_or
                    | logical_or CONDOP expression COLON conditional
additive            : multiplicative
                    | additive (PLUS|MINUS) multiplicative
multiplicative      : unary
                    | multiplicative (TIMES|DEVIDE|MOD) unary
unary               : primary
                    | (PLUS|MINUS|NOT|LNOT) unary
primary             : INT_CONST_DEC
                    | LPAREN expression RPAREN
equality            : relational
                    | equality (EQ|NE) relational
relational          : additive
                    | relational (LT|GT|LE|GE) additive
logical_or          : logical_and
                    | logical_or LOR logical_and
logical_and         : equality
                    | logical_and LAND equality
"""


class NanoParser():
    def __init__(self):
        pass

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def p_prog_func(self, p):
        'program    : function'
        p[0] = ProgNode(p[1])

    def p_func_def(self, p):
        'function   : type ID LPAREN RPAREN curl_block'
        p[0] = FuncNode(p[1], p[2], p[5])

    def p_type_def(self, p):
        'type       : INT'
        p[0] = TypeNode(p[1])

    def p_stmt_ret_exp(self, p):
        'statement  : RETURN expression SEMI'
        p[0] = RetNode(p[2])

    def p_pass_on_first(self, p):
        '''
        statement       : expression SEMI
        ctrl_block      : curl_block
        ctrl_block      : statement
        expression      : assignment
        assignment      : conditional
        conditional     : logical_or
        logical_or      : logical_and
        logical_and     : equality
        additive        : multiplicative
        multiplicative  : unary
        unary           : primary
        equality        : relational
        relational      : additive
        statement       : declaration
        '''
        p[0] = p[1]

    def p_pass_on_second(self, p):
        '''
        typeinit        : EQUALS expression
        curl_block      : LBRACE block RBRACE
        '''
        p[0] = p[2]

    def p_stmt_semi(self, p):
        'statement : SEMI'
        pass

    def p_if_stmt(self, p):
        '''statement : IF LPAREN expression RPAREN ctrl_block
                     | IF LPAREN expression RPAREN ctrl_block ELSE ctrl_block
        '''
        if len(p) > 6:
            p[0] = IfStmtNode(p[3], p[5], p[7])  # with else statement
        else:
            p[0] = IfStmtNode(p[3], p[5], None)  # no else statement

    def p_cond_exp(self, p):
        'conditional : logical_or CONDOP expression COLON conditional'
        # TODO: construct conditional node

    def p_declaration(self, p):
        '''
        declaration    : type declist SEMI
        '''
        if isinstance(p[2], DecListNode):
            for dec in p[2].declist:
                dec.type = p[1]
        else:
            p[2].type = p[1]
        p[0] = p[2]

    def p_assignment(self, p):
        '''
        assignment : ID EQUALS expression
        '''
        p[0] = AssNode(p[1], p[3])

    def p_prim_exp(self, p):
        'primary : LPAREN expression RPAREN'
        p[0] = PrimNode(p[2])

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
        block        :
        typeinit     :
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

    def p_dec_list(self, p):
        '''
        declist     : declist COMMA ID typeinit
        '''
        if isinstance(p[1], DecNode):
            dec = p[1]
            p[1] = DecListNode()
            p[1].append(dec)
        p[1].append(DecNode(None, p[3], p[4]))
        p[0] = p[1]

    def p_dec_init(self, p):
        '''
        declist     : ID typeinit
        '''
        p[0] = DecNode(None, p[1], p[2])

    # Error rule for syntax errors

    def p_error(self, p):
        print(colored("Error: ", "red")+"Syntax error when parsing "+str(p))

    def parse(self, input, **kwargs) -> Node:
        try:
            return self.parser.parse(input, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(colored("Error: ", "red")+f"{e}")

    tokens = NanoLexer.tokens
    precidence = {
        
    }


if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        lexer.build()
        parser = NanoParser()
        parser.build()
        root = parser.parse(content, debug=0)
        print(colored("Tree: ", 'yellow', attrs=['bold']) + str(root))
