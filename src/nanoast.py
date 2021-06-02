from typing import List


class Node(object):
    # A simple Abstract Syntax Tree node
    def accept(self, visitor):
        pass


"""
program    : function
function   : type ID LPAREN RPAREN LBRACE statement RBRACE
type       : INT
statement  : RETURN expression SEMI

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



class TypeNode(Node):
    def __init__(self, typestr: str):
        self.typestr = typestr

    def __str__(self):
        return f"({self.__class__.__name__}: {self.typestr})"


class ExpNode(Node):
    def __init__(self, node: Node):
        self.node = node

    def __str__(self):
        return f"({self.__class__.__name__}: {self.node})"


class PrimNode(Node):
    def __init__(self, node: Node):
        self.node = node

    def __str__(self):
        return f"({self.__class__.__name__}: {self.node}"


class StmtNode(Node):
    def __init__(self, exp: ExpNode):
        self.exp = exp

    def __str__(self):
        return f"({self.__class__.__name__}: RETURN {self.exp};)"


class FuncNode(Node):
    def __init__(self, type: TypeNode, id: str, stmt: StmtNode):
        self.type, self.id, self.stmt = type, id, stmt

    def __str__(self):
        return f"""({self.__class__.__name__}: {self.type} {self.id}()
""" + "    {" + f"""
    {self.stmt}
""" + "    })"

    def accept(self, visitor):
        return visitor.visitFunction(self)


class ProgNode(Node):
    # A simple Abstract Syntax Tree for the whole program
    # currently, the program only supports a function
    def __init__(self, func: FuncNode):
        assert func.id == "main", "No main function defined for program"
        self.func = func

    def __str__(self):
        return f"""
    ({self.__class__.__name__}:
    {self.func})
"""

    def accept(self, visitor):
        return visitor.visitProgram(self)


class IntNode(Node):
    def __init__(self, value: int):
        assert value <= 2**31 - 1 and value >= 0, f"{value} is out of integer range"
        self.value = value

    def __str__(self):
        return f"({self.__class__.__name__}: {self.value})"

    def accept(self, visitor):
        return visitor.visitIntNode(self)


class UnaryNode(Node):
    _legal_ops = {*"+-!~"}

    def __init__(self, op: str, node: Node):
        assert op in UnaryNode._legal_ops
        self.op, self.node = op, node

    def __str__(self):
        return f"({self.__class__.__name__}: {self.op}{self.node})"


class BinopNode(Node):
    _legal_ops = {*"+-*/%<>", '==', '!=', '<=', '>=', '||', '&&'}

    def __init__(self, op: str, left: Node, right: Node):
        assert op in BinopNode._legal_ops
        self.op, self.left, self.right = op, left, right

    def __str__(self):
        return f"({self.__class__.__name__}: {self.left} {self.op} {self.right})"

    def accept(self, visitor):
        return visitor.visitBinopNode(self)


class Visitor:
    def visitIntNode(self, node: IntNode):
        pass

    def visitBinopNode(self, node: BinopNode):
        node.left.accept(self)
        node.right.accept(self)


class NanoVisitor(Visitor):
    def __init__(self):
        self.result_dict = {}  # Node -> int

    def cache_result(visit):  # decorator
        def wrapped(self, node):
            if node in self.result_dict:
                return self.result_dict[node]
            value = visit(self, node)
            print(f"Getting: {value}({type(value)})")
            self.result_dict[node] = value
            return value
        return wrapped

    @cache_result
    def visitIntNode(self, node: IntNode):
        return node.value

    @cache_result
    def visitBinopNode(self, node: BinopNode):
        lhs = node.left.accept(self)
        rhs = node.right.accept(self)
        if node.op == "+":
            return lhs + rhs
        if node.op == "-":
            return lhs - rhs
        if node.op == "*":
            return lhs * rhs
        if node.op == "/":
            return lhs / rhs
        if node.op == "%":
            return lhs % rhs
