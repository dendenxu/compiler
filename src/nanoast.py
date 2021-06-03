from typing import List
from termcolor import colored

class Node(object):
    # A simple Abstract Syntax Tree node
    TABSTR = '|   '

    def __init__(self):
        self.indentLevel = 0

    def accept(self, visitor):
        pass

#############################################################
#                   Constant Literals/ID                    #
#############################################################


class IDNode(Node):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def accept(self, visitor):
        return visitor.visitIDNode(self)


class LiteralNode(Node):
    pass


class IntNode(LiteralNode):
    def __init__(self, value: int):
        assert value <= 2**31 - 1 and value >= 0, \
            f"{value} is out of integer range"
        super().__init__()
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"

    def accept(self, visitor):
        return visitor.visitIntNode(self)


class FloatNode(LiteralNode):
    def __init__(self, value: float):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"


class CharNode(LiteralNode):
    def __init__(self, value: str):
        assert len(value) == 1, "Char literal should only have a length of 1"
        super().__init__()
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"


class StringNode(LiteralNode):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"


#############################################################
#                           Typing                          #
#############################################################

class TypeNode(Node):
    def __init__(self, typestr: str):
        super().__init__()
        self.typestr = typestr

    def __str__(self):
        return f"{self.__class__.__name__}({self.typestr})"

    def accept(self, visitor):
        return visitor.visitTypeNode(self)


#############################################################
#                    Program/Function                       #
#############################################################
class ParamNode(Node):
    def __init__(self, type: TypeNode, id: IDNode):
        self.type, self.id = type, id

    def __str__(self):
        return f"{self.__class__.__name__}({self.type} {self.id})"


class FuncNode(Node):
    def __init__(self, type: TypeNode, id: IDNode, params: List[ParamNode], block: Node):
        super().__init__()
        self.type, self.id, self.params, self.block = type, id, params, block

    def __str__(self):
        self.block.indentLevel = self.indentLevel + 1
        return self.TABSTR * self.indentLevel + colored(f"{self.__class__.__name__}", color='green', attrs=['bold']) + \
            f"( {self.type} {self.id}( {', '.join(list(map(str, self.params)))} )" + \
            f" {{ {self.block}\n" + self.TABSTR * self.indentLevel + "} )EndFunc\n" + self.TABSTR

    def accept(self, visitor):
        return visitor.visitFuncNode(self)


class ProgNode(Node):
    # A simple Abstract Syntax Tree for the whole program
    # currently, the program only supports a function
    def __init__(self, *args):
        # assert func.id.name == "main", "No main function defined for program"
        super().__init__()
        self.funcs = [*args]

    def append(self, func: FuncNode):
        self.funcs.append(func)

    def __str__(self):
        for f in self.funcs:
            f.indentLevel = self.indentLevel + 1
        return f"\n{self.__class__.__name__}(\n" + "\n".join(list(map(str, self.funcs))) + "\n)EndProg"

    def accept(self, visitor):
        return visitor.visitProgNode(self)


#############################################################
#                        Expression                         #
#############################################################

class ExpNode(Node):
    pass


class CallNode(ExpNode):
    def __init__(self, id: IDNode, params: List[ExpNode]):
        super().__init__()
        self.id, self.params = id, params

    def __str__(self):
        return f"{self.__class__.__name__}( {self.id}({', '.join(map(str, self.params))}) )"


class UnaryNode(ExpNode):
    _legal_ops = {*"+-!~"}

    def __init__(self, op: str, node: Node):
        assert op in UnaryNode._legal_ops
        super().__init__()
        self.op, self.node = op, node

    def __str__(self):
        return f"{self.__class__.__name__}( {self.op}{self.node} )"


class BinopNode(ExpNode):
    _legal_ops = {*"+-*/%<>", '==', '!=', '<=', '>=', '||', '&&'}

    def __init__(self, op: str, left: Node, right: Node):
        assert op in BinopNode._legal_ops
        super().__init__()
        self.op, self.left, self.right = op, left, right

    def __str__(self):
        return f"{self.__class__.__name__}( {self.left} {self.op} {self.right} )"

    def accept(self, visitor):
        return visitor.visitBinopNode(self)


#############################################################
#                         Statement                         #
#############################################################

class StmtNode(Node):
    def __str__(self):
        return f"{self.__class__.__name__}()"


class BlockNode(Node):

    def __init__(self, *args):
        # self.indentLevel = 2
        super().__init__()
        self.stmts = [*args]

    def append(self, node: StmtNode):
        self.stmts.append(node)

    def __str__(self):
        for item in self.stmts:
            item.indentLevel = self.indentLevel + 1
        return colored(f'{self.__class__.__name__}({self.indentLevel}\n', color='cyan', attrs=['bold']) + \
            self.TABSTR * self.indentLevel + \
            ('\n' + self.TABSTR * self.indentLevel).join(list(map(str, self.stmts))) + \
            '\n' + self.TABSTR * (self.indentLevel - 1) + colored(f')EndBlock{self.indentLevel}', color='magenta', attrs=['bold'])

    def accept(self, visitor):
        return visitor.visitBlockNode(self)


class AssNode(StmtNode):

    def __init__(self, id: IDNode, exp: ExpNode):
        super().__init__()
        self.id, self.exp = id, exp

    def __str__(self):
        return f"{self.__class__.__name__}( {self.id} = {self.exp} )"

    def accept(self, visitor):
        return visitor.visitAssNode(self)


class DecNode(StmtNode):

    def __init__(self, type: TypeNode, id: IDNode, init: Node):
        # init might be none
        super().__init__()
        self.type, self.id, self.init = type, id, init

    def __str__(self):
        return f"{self.__class__.__name__}( {self.type} {self.id}" + (f' = {self.init}' if self.init is not None else '') + ' )'

    def accept(self, visitor):
        return visitor.visitDecNode(self)


class RetNode(StmtNode):
    def __init__(self, exp: ExpNode):
        super().__init__()
        self.exp = exp

    def __str__(self):
        return f"{self.__class__.__name__}( RETURN {self.exp}; )"

    def accept(self, visitor):
        return visitor.visitRetNode(self)


class IfStmtNode(StmtNode):

    def __init__(self, cond: ExpNode, ifbody: BlockNode, elsebody: BlockNode = None):
        super().__init__()
        self.cond = cond
        self.ifbody = ifbody
        self.elsebody = elsebody  # this can be None if this if stmt is not paired with a else statement

    def __str__(self):
        self.ifbody.indentLevel = self.elsebody.indentLevel = self.indentLevel
        return f"{self.__class__.__name__}( IF ({self.cond}) {{ {self.ifbody} }} ELSE {{ {self.elsebody} }} )"

    def accept(self, visitor):
        return visitor.visitIfStmtNode(self)


class LoopNode(StmtNode):

    def __init__(self, pre: BlockNode, cond: ExpNode, body: BlockNode, post: BlockNode):
        super().__init__()
        self.pre, self.cond, self.body, self.post = pre, cond, body, post

    def __str__(self):
        self.pre.indentLevel = self.body.indentLevel = self.post.indentLevel = self.indentLevel
        return f"{self.__class__.__name__}( {self.pre} LOOP({self.cond}) {{ {self.body}, {self.post} }} )"

    def accept(self, visitor):
        return visitor.visitLoopNode(self)


class BreakNode(StmtNode):
    pass


class ContinueNode(StmtNode):
    pass
