from ply import yacc
from nanolex import NanoLexer
from nanoast import *
import sys
from termcolor import colored
import traceback

""" 
Productions used in the parser:

program             : program function
                    |
function            : type ID LPAREN parameters RPAREN curl_block
parameters          : type ID
                    | paramters COMMA type ID
                    |
block               : block curl_block
                    | block statement
                    | 
type                : INT
                    | VOID
                    | LONG
                    | FLOAT
                    | DOUBLE
                    | CHAR
statement           : RETURN expression SEMI
                    | expression SEMI
                    | declaration
                    | IF LPAREN expression RPAREN ctrl_block ELSE ctrl_block
                    | IF LPAREN expression RPAREN ctrl_block
                    | FOR LPAREN for_init RPAREN ctrl_block
                    | WHILE LPAREN expression RPAREN ctrl_block
                    | DO ctrl_block WHILE LPAREN expression RPAREN SEMI
                    | BREAK SEMI
                    | CONTINUE SEMI
                    | SEMI
for_init            : e_expression SEMI e_expression SEMI e_expression
                    | declaration e_expression SEMI e_expression
expression_list     : expression_list expression
                    | expression
                    |
e_expression        : expression
                    | 
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
unary               : postfix
                    | (PLUS|MINUS|NOT|LNOT) unary
postfix             : primayr
                    | ID LPAREN expression_list RPAREN
primary             : INT_CONST_DEC
                    | FLOAT_CONST
                    | CHAR_CONST
                    | STRING_LITERAL
                    | ID
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
        'program    : program function'
        if p[1] is None:
            p[1] = ProgNode()
        p[1].append(p[2])  # init to a function
        p[0] = p[1]

    def p_func_def(self, p):
        'function   : type ID LPAREN parameters RPAREN curl_block'
        p[0] = FuncNode(p[1], IDNode(p[2]), p[4], p[6])

    def p_param(self, p):
        'parameters : type ID'
        p[0] = ParamListNode(ParamNode(p[1], IDNode(p[2])))

    def p_params(self, p):
        'parameters : parameters COMMA type ID'
        param = ParamNode(p[3], IDNode(p[4]))
        p[1].append(param)
        p[0] = p[1]

    def p_type_def(self, p):
        '''
        type    : INT
                | VOID
                | LONG
                | FLOAT
                | DOUBLE
                | CHAR
        '''
        p[0] = TypeNode(p[1])

    def p_stmt_ret_exp(self, p):
        'statement  : RETURN expression SEMI'
        p[0] = RetNode(p[2])

    def p_pass_on_first(self, p):
        '''
        statement       : expression SEMI
        e_expression    : expression
        ctrl_block   : curl_block
        expression      : assignment
        assignment      : conditional
        conditional     : logical_or
        logical_or      : logical_and
        logical_and     : equality
        additive        : multiplicative
        multiplicative  : unary
        unary           : postfix
        postfix         : primary
        equality        : relational
        relational      : additive
        statement       : declaration
        '''
        p[0] = p[1]

    def p_ctrl_block_wrap(self, p):
        'ctrl_block     : statement'
        # control block should wrap up the single statment as a block
        # for scope construction
        p[0] = BlockNode(p[1])

    def p_pass_on_second(self, p):
        '''
        typeinit        : EQUALS expression
        curl_block      : LBRACE block RBRACE
        '''
        p[0] = p[2]

    def p_params_empty(self, p):
        'parameters   :'
        p[0] = ParamListNode()

    def p_break(self, p):
        'statement : BREAK SEMI'
        p[0] = BreakNode()

    def p_continue(self, p):
        'statement : CONTINUE SEMI'
        p[0] = ContinueNode()

    def p_stmt_empty(self, p):
        '''
        statement : SEMI
        e_expression :
        '''
        p[0] = StmtNode()  # empty statment node

    def p_if_stmt(self, p):
        '''statement : IF LPAREN expression RPAREN ctrl_block
                     | IF LPAREN expression RPAREN ctrl_block ELSE ctrl_block
        '''
        # ! Dangling ELSE problem exists, but doesn't affect the grammar
        # ! relying on the generated parser feature of preferring shift over reduce whenever there is a conflict.
        if len(p) > 6:
            p[0] = IfStmtNode(p[3], p[5], p[7])  # with else statement
        else:
            p[0] = IfStmtNode(p[3], p[5], StmtNode())  # no else statement

    def p_while_stmt(self, p):
        'statement : WHILE LPAREN expression RPAREN ctrl_block'
        p[0] = LoopNode(StmtNode(), p[3], p[5], StmtNode())  # simple while loop

    def p_do_while_stmt(self, p):
        'statement : DO ctrl_block WHILE LPAREN expression RPAREN SEMI'
        p[0] = LoopNode(p[3], p[3], p[5], StmtNode())  # simple do-while loop

    def p_for_stmt(self, p):
        '''
        statement : FOR LPAREN for_init RPAREN ctrl_block
        '''
        # assuming a BlockNode from for_init
        init = p[3].stmts
        p[0] = LoopNode(init[0], init[1], p[5], init[2])

    def p_for_init(self, p):
        '''
        for_init   : e_expression SEMI e_expression SEMI e_expression
                   | declaration e_expression SEMI e_expression
        '''
        p[0] = BlockNode()
        if len(p) == 6:  # with e_expression
            p[0].append(p[1])  # initialization
            p[0].append(p[3])  # break condition
            p[0].append(p[5])  # operation at loopend
        else:  # with declaration
            p[0].append(p[1])  # initialization
            p[0].append(p[2])  # break condition
            p[0].append(p[4])  # operation at loopend

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
        p[0] = AssNode(IDNode(p[1]), p[3])

    def p_prim_exp(self, p):
        'primary : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_prim_int(self, p):
        'primary      : INT_CONST_DEC'
        p[0] = IntNode(int(p[1]))

    def p_prim_float(self, p):
        'primary      : FLOAT_CONST'
        p[0] = FloatNode(float(p[1]))

    def p_prim_char(self, p):
        'primary      : CHAR_CONST'
        p[0] = CharNode(p[1])

    def p_prim_string(self, p):
        'primary      : STRING_LITERAL'
        p[0] = StringNode(str(p[1]))

    def p_prim_id(self, p):
        'primary : ID'
        p[0] = IDNode(p[1])

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
        program      :
        '''
        p[0] = None

    def p_block_stmt(self, p):
        '''
        block       : block curl_block
                    | block statement
        '''
        if p[1] is None:
            p[1] = BlockNode()
        if isinstance(p[2], DecListNode):
            for dec in p[2].declist:
                p[1].append(dec)
        else:
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
        p[1].append(DecNode(None, IDNode(p[3]), p[4]))
        p[0] = p[1]

    def p_dec_init(self, p):
        '''
        declist     : ID typeinit
        '''
        p[0] = DecNode(None, IDNode(p[1]), p[2])

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
