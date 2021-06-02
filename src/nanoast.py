from typing import List


class Node(object):
    # A simple Abstract Syntax Tree node
    def accept(self, visitor):
        pass

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


class RetNode(Node):
    def __init__(self, exp: ExpNode):
        self.exp = exp

    def __str__(self):
        return f"({self.__class__.__name__}: RETURN {self.exp};)"


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


class BlockNode(Node):

    def __init__(self):
        self.stmts = []

    def append(self, node: StmtNode):
        self.stmts.append(node)

    def __str__(self):
        return f'({self.__class__.__name__}:\n'+'    '*2+('\n'+2*'    ').join(map(str, self.stmts)) + ')'


class AssNode(Node):

    def __init__(self, id: str, exp: ExpNode):
        self.id, self.exp = id, exp

    def __str__(self):
        return f"({self.__class__.__name__}: {self.id} = {self.exp})"


class DecNode(Node):

    def __init__(self, type: TypeNode, id: str, init: Node):
        # init might be none
        self.type, self.id, self.init = type, id, init

    def __str__(self):
        return f"({self.__class__.__name__}: {self.type} {self.id}" + (f' = {self.init}' if self.init is not None else '') + ")"


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
