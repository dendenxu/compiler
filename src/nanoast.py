from typing import List


class Node(object):
    # A simple Abstract Syntax Tree node
    def accept(self, visitor):
        pass


class TypeNode(Node):
    def __init__(self, typestr: str):
        self.typestr = typestr

    def __str__(self):
        return f"{self.__class__.__name__}({self.typestr})"

    def accept(self, visitor):
        return visitor.visitTypeNode(self)


class ExpNode(Node):
    def __init__(self, node: Node):
        self.node = node

    def __str__(self):
        return f"{self.__class__.__name__}( {self.node} )"


class PrimNode(Node):
    def __init__(self, node: Node):
        self.node = node

    def __str__(self):
        return f"{self.__class__.__name__}( {self.node} )"

    def accept(self, visitor):
        return visitor.visitPrimNode(self)


class RetNode(Node):
    def __init__(self, exp: ExpNode):
        self.exp = exp

    def __str__(self):
        return f"{self.__class__.__name__}( RETURN {self.exp}; )"

    def accept(self, visitor):
        return visitor.visitRetNode(self)


class FuncNode(Node):
    def __init__(self, type: TypeNode, id: str, block: Node):
        self.type, self.id, self.block = type, id, block

    def __str__(self):
        return f"{self.__class__.__name__}( {self.type} {self.id}()" + \
            " {" + f"\n    {self.block}\n" + "    } )EndFunc\n"

    def accept(self, visitor):
        return visitor.visitFuncNode(self)


class ProgNode(Node):
    # A simple Abstract Syntax Tree for the whole program
    # currently, the program only supports a function
    def __init__(self, func: FuncNode):
        assert func.id == "main", "No main function defined for program"
        self.func = func

    def __str__(self):
        return f"""
{self.__class__.__name__}(
    {self.func} 
)EndProg
"""

    def accept(self, visitor):
        return visitor.visitProgNode(self)


class IntNode(Node):
    def __init__(self, value: int):
        assert value <= 2**31 - 1 and value >= 0, \
            f"{value} is out of integer range"
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"

    def accept(self, visitor):
        return visitor.visitIntNode(self)


class UnaryNode(Node):
    _legal_ops = {*"+-!~"}

    def __init__(self, op: str, node: Node):
        assert op in UnaryNode._legal_ops
        self.op, self.node = op, node

    def __str__(self):
        return f"{self.__class__.__name__}( {self.op}{self.node} )"


class BinopNode(Node):
    _legal_ops = {*"+-*/%<>", '==', '!=', '<=', '>=', '||', '&&'}

    def __init__(self, op: str, left: Node, right: Node):
        assert op in BinopNode._legal_ops
        self.op, self.left, self.right = op, left, right

    def __str__(self):
        return f"{self.__class__.__name__}( {self.left} {self.op} {self.right} )"

    def accept(self, visitor):
        return visitor.visitBinopNode(self)


class BlockNode(Node):

    def __init__(self, *args):
        self.stmts = [*args]

    def append(self, node: Node):
        self.stmts.append(node)

    def __str__(self):
        return f'{self.__class__.__name__}(\n' + 2*'    ' + \
            ('\n' + 2*'    ').join(list(map(str, self.stmts))) + \
            '\n    )EndBlock'

    def accept(self, visitor):
        return visitor.visitBlockNode(self)


class AssNode(Node):

    def __init__(self, id: str, exp: ExpNode):
        self.id, self.exp = id, exp

    def __str__(self):
        return f"{self.__class__.__name__}( {self.id} = {self.exp} )"

    def accept(self, visitor):
        return visitor.visitAssNode(self)

class DecNode(Node):

    def __init__(self, type: TypeNode, id: str, init: Node):
        # init might be none
        self.type, self.id, self.init = type, id, init

    def __str__(self):
        return f"{self.__class__.__name__}( {self.type} {self.id}" + (f' = {self.init}' if self.init is not None else '') + ' )'

    def accept(self, visitor):
        return visitor.visitDecNode(self)


class DecListNode(Node):

    def __init__(self):
        self.declist = []

    def append(self, node: DecNode):
        self.declist.append(node)

    def __str__(self):
        return f'{self.__class__.__name__}(\n' + '    '*3 + \
            ('\n'+3*'    ').join(map(str, self.declist)) + ' )'

    def accept(self, visitor):
        return visitor.visitDecListNode(self)


class IfStmtNode(Node):

    def __init__(self, exp: ExpNode, ifnode: BlockNode, elsenode: BlockNode = None):
        self.exp = exp
        self.ifnode = ifnode
        self.elsenode = elsenode  # this can be None if this if stmt is not paired with a else statement

    def __str__(self):
        return f"{self.__class__.__name__}( IF ({self.exp}) {{ {self.ifnode} }} ELSE {{ {self.elsenode} }} )"
    
    def accept(self, visitor):
        return visitor.visitIfStmtNode(self)

class LoopNode(Node):

    def __init__(self, pre: BlockNode, cond: ExpNode, body: BlockNode, post: BlockNode):
        self.pre, self.cond, self.body, self.post = pre, cond, body, post
    
    def __str__(self):
        return f"{self.__class__.__name__}( {self.pre} LOOP({self.cond}) {{ {self.cond}\b{self.post} }} )"

    def accept(self, visitor):
        return visitor.visitLoopNode(self)
