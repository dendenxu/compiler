from ply import yacc
import sys
from termcolor import colored
import traceback
from nanotraverse import *
from nanolex import *
from nanoast import *
import requests
import json


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


class NanoParser():
    ########################################################
    ###                                                  ###
    ###                      PROGRAM                     ###
    ###                                                  ###
    ########################################################

    #############################################################
    #                The Whole C File (Functions)               #
    #############################################################

    def p_prog_func(self, p):
        # program can have multiple functions
        # and global variable definitions
        '''
        program             : program function
                            | program declaration
        '''
        if p[1] is None:
            p[1] = ProgNode()
            p[1].update_pos(p.lineno(0), self._find_tok_column(p.lexpos(0)))
        if isinstance(p[2], list):
            for dec in p[2]:
                p[1].append(dec)
        else:
            p[1].append(p[2])
        p[0] = p[1]

    #############################################################
    #                     Function Definition                   #
    #############################################################

    def p_func_def(self, p):
        '''
        function            : type id LPAREN param_list RPAREN curl_block
        '''
        p[0] = FuncNode(p[1], p[2], p[4], p[6])
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_params(self, p):
        '''
        param_list          : type id comma_params
        '''
        param = ParamNode(p[1], p[2])
        param.update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))
        if p[3] is None:
            p[3] = []
        p[3] = [param] + p[3]
        p[0] = p[3]

    def p_comma_params(self, p):
        '''
        comma_params        : comma_params COMMA type id
        '''
        param = ParamNode(p[3], p[4])
        param.update_pos(p.lineno(3), self._find_tok_column(p.lexpos(3)))
        if p[1] is None:
            p[1] = []
        p[1].append(param)
        p[0] = p[1]

    ########################################################
    ###                                                  ###
    ###                     STATEMENT                    ###
    ###                                                  ###
    ########################################################

    #############################################################
    #                      Scope Resolution                     #
    #############################################################

    def p_ctrl_block_wrap(self, p):
        '''
        ctrl_block          : statement
        '''
        # control block should wrap up the single statment as a block
        # for scope construction
        p[0] = BlockNode(p[1])
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_block_stmt(self, p):
        '''
        block               : block curl_block
                            | block statement
        '''
        if p[1] is None:
            p[1] = BlockNode()
            p[1].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))
        if isinstance(p[2], list):
            for dec in p[2]:
                p[1].append(dec)
        else:
            p[1].append(p[2])
        p[0] = p[1]

    #############################################################
    #                    Variable Declaration                   #
    #############################################################

    def p_declaration(self, p):
        '''
        declaration         : type dec_list SEMI
        '''
        if isinstance(p[2], list):
            for dec in p[2]:
                dec.type = p[1]
                dec.update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))
        else:
            p[2].type = p[1]
            p[2].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))
        p[0] = p[2]

    def p_dec_arr_list(self, p):
        '''
        array_list          : array_list LBRACKET INT_CONST_DEC RBRACKET
        '''
        p[1].append(int(p[3]))  # should always be an array
        p[0] = p[1]

    def p_dec_list(self, p):
        '''
        dec_list            : dec_list COMMA id array_list typeinit
        '''
        if isinstance(p[1], DecNode):
            dec = p[1]
            p[1] = []
            p[1].append(dec)
        dec = DecNode(None, p[3], p[4], p[5])
        dec.update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))
        p[1].append(dec)
        p[0] = p[1]

    def p_dec_init(self, p):
        '''
        dec_list            : id array_list typeinit
        '''
        p[0] = DecNode(None, p[1], p[2], p[3])
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    #############################################################
    #                      Single Statements                    #
    #############################################################

    def p_stmt_ret_exp(self, p):
        '''
        statement           : RETURN empty_or_exp SEMI
        '''
        p[0] = RetNode(p[2])
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_break_stmt(self, p):
        '''
        statement           : BREAK SEMI
        '''
        p[0] = BreakNode()
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_continue_stmt(self, p):
        '''
        statement           : CONTINUE SEMI
        '''
        p[0] = ContinueNode()
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_stmt_empty(self, p):
        '''
        statement           : SEMI
        '''
        p[0] = EmptyStmtNode()  # empty statment node
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    #############################################################
    #                         Control Flow                      #
    #############################################################

    def p_if_stmt(self, p):
        '''statement        : IF LPAREN expression RPAREN ctrl_block
                            | IF LPAREN expression RPAREN ctrl_block ELSE ctrl_block
        '''
        # ! Dangling ELSE problem exists, but doesn't affect the grammar
        # ! relying on the generated parser feature of preferring shift over reduce whenever there is a conflict.
        if len(p) > 6:
            p[0] = IfStmtNode(p[3], p[5], p[7])  # with else statement
        else:
            p[0] = IfStmtNode(p[3], p[5], EmptyStmtNode())  # no else statement
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_while_stmt(self, p):
        '''
        statement           : WHILE LPAREN expression RPAREN ctrl_block
        '''
        p[0] = LoopNode(EmptyStmtNode(), p[3], p[5], EmptyStmtNode())  # simple while loop
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_do_while_stmt(self, p):
        '''
        statement           : DO ctrl_block WHILE LPAREN expression RPAREN SEMI
        '''
        p[0] = LoopNode(p[2], p[3], p[5], EmptyStmtNode())  # simple do-while loop
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_for_stmt(self, p):
        '''
        statement           : FOR LPAREN for_init RPAREN ctrl_block
        '''
        # assuming a BlockNode from for_init
        init = p[3]
        p[0] = LoopNode(init[0], init[1], p[5], init[2])
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_for_init(self, p):
        '''
        for_init            : empty_or_exp SEMI empty_or_exp SEMI empty_or_exp
                            | declaration empty_or_exp SEMI empty_or_exp
        '''
        if len(p) == 6:  # with empty_or_exp
            p[0] = [
                p[1],  # initialization
                p[3],  # break condition
                p[5],  # operation at loopend
            ]
        else:  # with declaration
            p[0] = [
                p[1],  # initialization
                p[2],  # break condition
                p[4],  # operation at loopend
            ]

    ########################################################
    ###                                                  ###
    ###                     EXPRESSION                   ###
    ###                                                  ###
    ########################################################

    #############################################################
    #                      Single Expression                    #
    #############################################################

    def p_exp_empty(self, p):
        '''
        empty_or_exp             : 
        '''
        p[0] = EmptyExpNode()  # empty expression node
        p[0].update_pos(p.lineno(0), self._find_tok_column(p.lexpos(0)))

    def p_cond_exp(self, p):
        '''
        conditional         : logical_or CONDOP expression COLON conditional
        '''
        p[0] = TernaryNode(p[1], p[2], p[3], p[4], p[5])
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    #############################################################
    #                           Assignment                      #
    #############################################################

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

    def p_unary_op(self, p):
        '''
        unary               : PLUS unary
                            | MINUS unary
                            | NOT unary
                            | LNOT unary
                            | TIMES unary
                            | AND unary
                            | LPAREN type RPAREN unary
        '''
        if len(p) == 3:  # ordinary unary operation
            p[0] = UnaryNode(p[1], p[2])
        else:
            p[0] = UnaryNode(p[2], p[4])  # note that p[2] is a TypeNode for type casting
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

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
        # Using pos of OP as the pos of the binary exp
        p[0].update_pos(p.lineno(2), self._find_tok_column(p.lexpos(2)))

    #############################################################
    #                     Array Subscription                    #
    #############################################################

    def p_arr_sub(self, p):
        '''
        postfix             : postfix LBRACKET expression RBRACKET
        '''
        p[0] = ArrSubNode(p[1], p[3])
        p[0].update_pos(p.lineno(2), self._find_tok_column(p.lexpos(2)))

    #############################################################
    #                       Function Call                       #
    #############################################################

    def p_call_func(self, p):
        '''
        postfix             : id LPAREN exp_list RPAREN
        '''
        p[0] = CallNode(p[1], p[3])
        p[0].update_pos(p.lineno(2), self._find_tok_column(p.lexpos(2)))

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

    ########################################################
    ###                                                  ###
    ###                     RESOLUTION                   ###
    ###                                                  ###
    ########################################################

    #############################################################
    #                      Constant Resolution                  #
    #############################################################

    def p_prim_int(self, p):
        '''
        primary             : INT_CONST_DEC
        '''
        p[0] = IntNode(int(p[1]))
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_prim_float(self, p):
        '''
        primary             : FLOAT_CONST
        '''
        p[0] = FloatNode(float(p[1]))
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_prim_char(self, p):
        '''
        primary             : CHAR_CONST
        '''
        p[0] = CharNode(p[1])
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    def p_prim_string(self, p):
        '''
        primary             : STRING_LITERAL
        '''
        p[0] = StringNode(str(p[1]))
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    #############################################################
    #                        Name Resolution                    #
    #############################################################

    def p_id(self, p):
        '''
        id                  : ID
        '''
        p[0] = IDNode(p[1])
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    #############################################################
    #                        Type Resolution                    #
    #############################################################

    def p_type_resolve(self, p):
        '''
        type                : INT
                            | VOID
                            | LONG
                            | FLOAT
                            | DOUBLE
                            | CHAR
                            | type TIMES
        '''
        p[0] = TypeNode(p[1])  # nested type: pointers
        p[0].update_pos(p.lineno(1), self._find_tok_column(p.lexpos(1)))

    ########################################################
    ###                                                  ###
    ###                       PARSING                    ###
    ###                                                  ###
    ########################################################

    #############################################################
    #                Convinient Parsing Utilities               #
    #############################################################

    def p_empty(self, p):
        '''
        typeinit            :
        program             :
        comma_params        : 
        comma_exps          :
        '''
        p[0] = None

    def p_empty_spec(self, p):
        '''
        block               :
        '''
        p[0] = BlockNode()
        p[0].update_pos(p.lineno(0), self._find_tok_column(p.lexpos(0)))

    def p_empty_list(self, p):
        '''
        exp_list            :
        param_list          :
                            | VOID
        array_list          :
        '''
        p[0] = []

    def p_pass_on_first(self, p):
        '''
        statement           : declaration
        statement           : expression SEMI
        empty_or_exp        : expression
        ctrl_block          : curl_block
        expression          : assignment
        assignment          : conditional
        conditional         : logical_or
        logical_or          : logical_and
        logical_and         : bitwise_or
        bitwise_or          : bitwise_xor
        bitwise_xor         : bitwise_and
        bitwise_and         : equality
        equality            : relational
        relational          : shiftable
        shiftable           : additive
        additive            : multiplicative
        multiplicative      : unary
        unary               : postfix
        postfix             : primary
        primary             : id
        '''
        p[0] = p[1]

    def p_pass_on_second(self, p):
        '''
        typeinit            : EQUALS expression
        curl_block          : LBRACE block RBRACE
        primary             : LPAREN expression RPAREN
        '''
        p[0] = p[2]

    #############################################################
    #                      Syntax Error Rules                   #
    #############################################################

    def _find_tok_column(self, lexpos):
        """ Find the column of the given lexpos in its line.
            lexer.lexdata points to the input
        """
        last_cr = lex.lexer.lexdata.rfind('\n', 0, lexpos)
        return lexpos - last_cr

    def p_error(self, p):
        # with a syntax error, the token should contain corresponding location
        # errLine = p.lineno(0)
        # errCol = self._find_tok_column(p.lexpos(0))
        print(colored(f"Error: ", "red") + "Syntax error when parsing " + str(p))

    #############################################################
    #                      External Functions                   #
    #############################################################

    def parse(self, input, **kwargs) -> Node:
        try:
            return self.parser.parse(input, tracking=True, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(colored("Error: ", "red")+f"{e}")

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    tokens = NanoLexer.tokens


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
        # Print Struct Tree (data sent to server)
        # print(colored("Structrued Tree: ", 'yellow', attrs=['bold']))
        # print(tree)
        addinfo(tree, args.input)
        payload = json.dumps(tree)

        if args.tree:
            with open(args.tree, 'w') as f:
                f.write(payload)
            print(colored(f"Saved Structrued Tree to {args.tree}", 'yellow', attrs=['bold']))

        r = requests.post(url=args.url, data=payload)
        print(colored(f"POST response: {r}", "yellow", attrs=["bold"]))
