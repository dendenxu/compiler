import sys
from ply import lex
from termcolor import colored


class NanoLexer():
    """ A lexer for the Nano C language. After building it, set the
        input text with input(), and call token() to get new
        tokens.
    """

    def __init__(self):
        """ Create a new Lexer

            Builds the lexer from the specification. Must be
            called after the lexer object is created.
            This method exists separately, because the PLY
            manual warns against calling lex.lex inside
            __init__
        """
        # Keeps track of the last token returned from self.token()
        self.last_token = None

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def reset_lineno(self):
        """ Resets the internal line number counter of the lexer.
        """
        self.lexer.lineno = 1

    def input(self, text):
        """ set the input to text
        """
        self.lexer.input(text)

    def token(self):
        """ get a new token from lexer
        """
        self.last_token = self.lexer.token()
        return self.last_token

    def find_tok_column(self, token):
        """ Find the column of the token in its line.
            lexer.lexdata points to the input
        """
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr

    """ ================== PRIVATE ================== """

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_tok_location(token)
        print(f"{colored('Fatal: ', 'red')}{msg} at {colored(f'{location}', 'magenta')}")
        self.lexer.skip(1)

    def _make_tok_location(self, token):
        return (token.lineno, self.find_tok_column(token))

    # Reserved keywords from C89
    # reference:
    # https://baike.baidu.com/item/%E4%BF%9D%E7%95%99%E5%85%B3%E9%94%AE%E5%AD%97/22045990?fr=aladdin
    keywords = (
        'INT', 'LONG', 'FLOAT', 'DOUBLE', 'CHAR',
        'UNSIGNED', 'CONST', 'VOID', "STATIC"
        'ENUM', 'STRUCT', 'UNION', 'IF', 'ELSE',
        'DO', 'WHILE', 'FOR', 'CONTINUE', 'BREAK', 'RETURN'
    )
    keyword_map = {}
    for keyword in keywords:
        keyword_map[keyword.lower()] = keyword

    # to be modified from here.....

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

    t_ignore = ' \t'

    # Define a rule so we can track line numbers
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    # Operators
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_OR = r'\|'
    t_AND = r'&'
    t_NOT = r'~'
    t_XOR = r'\^'
    t_LSHIFT = r'<<'
    t_RSHIFT = r'>>'
    t_LOR = r'\|\|'
    t_LAND = r'&&'
    t_LNOT = r'!'
    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_EQ = r'=='
    t_NE = r'!='

    # Assignment operators
    t_EQUALS = r'='
    t_TIMESEQUAL = r'\*='
    t_DIVEQUAL = r'/='
    t_MODEQUAL = r'%='
    t_PLUSEQUAL = r'\+='
    t_MINUSEQUAL = r'-='
    t_LSHIFTEQUAL = r'<<='
    t_RSHIFTEQUAL = r'>>='
    t_ANDEQUAL = r'&='
    t_OREQUAL = r'\|='
    t_XOREQUAL = r'\^='

    # Increment/decrement
    t_PLUSPLUS = r'\+\+'
    t_MINUSMINUS = r'--'

    # ->
    t_ARROW = r'->'

    # ?
    t_CONDOP = r'\?'

    # Delimeters
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','
    t_PERIOD = r'\.'
    t_SEMI = r';'
    t_COLON = r':'

    @lex.TOKEN(r'\{')
    def t_LBRACE(self, t):
        return t

    @lex.TOKEN(r'\}')
    def t_RBRACE(self, t):
        return t

    t_STRING_LITERAL = string_literal

    # The following floating and integer constants are defined as
    # functions to impose a strict order (otherwise, decimal
    # is placed before the others because its regex is longer,
    # and this is bad)
    #
    @lex.TOKEN(floating_constant)
    def t_FLOAT_CONST(self, t):
        return t

    @lex.TOKEN(decimal_constant)
    def t_INT_CONST_DEC(self, t):
        return t

    # Must come before bad_char_const, to prevent it from
    # catching valid char constants as invalid
    @lex.TOKEN(multicharacter_constant)
    def t_INT_CONST_CHAR(self, t):
        return t

    @lex.TOKEN(char_const)
    def t_CHAR_CONST(self, t):
        return t

    @lex.TOKEN(unmatched_quote)
    def t_UNMATCHED_QUOTE(self, t):
        msg = "Unmatched '"
        self._error(msg, t)

    @lex.TOKEN(identifier)
    def t_ID(self, t):
        t.type = self.keyword_map.get(t.value, "ID")
        return t

    def t_error(self, t):
        msg = 'Illegal character %s' % repr(t.value[0])
        self._error(msg, t)


if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        lexer.build()
        lexer.input(content)
        # Tokenize
        while True:
            tok = lexer.token()
            if not tok:
                break      # No more input
            print(tok)
