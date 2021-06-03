class Node(object):
    # A simple Abstract Syntax Tree node
    def accept(self, visitor):
        pass

#############################################################
#                   Constant Literals/ID                    #
#############################################################


class IDNode(Node):
    def __init__(self, name: str):
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
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"

    def accept(self, visitor):
        return visitor.visitIntNode(self)


class FloatNode(LiteralNode):
    def __init__(self, value: float):
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"


class CharNode(LiteralNode):
    def __init__(self, value: str):
        assert len(value) == 1, "Char literal should only have a length of 1"
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"


class StringNode(LiteralNode):
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"


#############################################################
#                           Typing                          #
#############################################################

class TypeNode(Node):
    def __init__(self, typestr: str):
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


class ParamListNode(Node):
    def __init__(self, *args):
        self.params = [*args]

    def append(self, param: ParamNode):
        self.params.append(param)

    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(list(map(str, self.params)))})"


class FuncNode(Node):
    def __init__(self, type: TypeNode, id: IDNode, params: ParamListNode, block: Node):
        self.type, self.id, self.params, self.block = type, id, params, block

    def __str__(self):
        return f"{self.__class__.__name__}( {self.type} {self.id}( {', '.join(list(map(str, self.params.params)))} )" + \
            " {" + f"\n    {self.block}\n" + "    } )EndFunc\n"

    def accept(self, visitor):
        return visitor.visitFuncNode(self)


class ProgNode(Node):
    # A simple Abstract Syntax Tree for the whole program
    # currently, the program only supports a function
    def __init__(self, *args):
        # assert func.id.name == "main", "No main function defined for program"
        self.funcs = [*args]

    def append(self, func: FuncNode):
        self.funcs.append(func)

    def __str__(self):
        return f"""
{self.__class__.__name__}(""" + \
            '\n'.join(list(map(str, self.funcs))) + \
            """)EndProg
"""

    def accept(self, visitor):
        return visitor.visitProgNode(self)


#############################################################
#                        Expression                         #
#############################################################

class ExpNode(Node):
    def __init__(self):
        pass


class ExpListNode(Node):
    def __init__(self, *args):
        self.exps = [*args]

    def append(self, exp: ExpNode):
        self.exps.append(exp)

    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(map(str, self.exps))})"


class CallNode(ExpNode):
    def __init__(self, id: IDNode, params: ExpListNode):
        self.id, self.params = id, params

    def __str__(self):
        return f"{self.__class__.__name__}({self.id}({self.params}))"


class UnaryNode(ExpNode):
    _legal_ops = {*"+-!~"}

    def __init__(self, op: str, node: Node):
        assert op in UnaryNode._legal_ops
        self.op, self.node = op, node

    def __str__(self):
        return f"{self.__class__.__name__}( {self.op}{self.node} )"


class BinopNode(ExpNode):
    _legal_ops = {*"+-*/%<>", '==', '!=', '<=', '>=', '||', '&&'}

    def __init__(self, op: str, left: Node, right: Node):
        assert op in BinopNode._legal_ops
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
        self.stmts = [*args]

    def append(self, node: StmtNode):
        self.stmts.append(node)

    def __str__(self):
        return f'{self.__class__.__name__}(\n' + 2*'    ' + \
            ('\n' + 2*'    ').join(list(map(str, self.stmts))) + \
            '\n    )EndBlock'

    def accept(self, visitor):
        return visitor.visitBlockNode(self)


class AssNode(StmtNode):

    def __init__(self, id: IDNode, exp: ExpNode):
        self.id, self.exp = id, exp

    def __str__(self):
        return f"{self.__class__.__name__}( {self.id} = {self.exp} )"

    def accept(self, visitor):
        return visitor.visitAssNode(self)


class DecNode(StmtNode):

    def __init__(self, type: TypeNode, id: IDNode, init: Node):
        # init might be none
        self.type, self.id, self.init = type, id, init

    def __str__(self):
        return f"{self.__class__.__name__}( {self.type} {self.id}" + (f' = {self.init}' if self.init is not None else '') + ' )'

    def accept(self, visitor):
        return visitor.visitDecNode(self)


class RetNode(StmtNode):
    def __init__(self, exp: ExpNode):
        self.exp = exp

    def __str__(self):
        return f"{self.__class__.__name__}( RETURN {self.exp}; )"

    def accept(self, visitor):
        return visitor.visitRetNode(self)


class DecListNode(StmtNode):

    def __init__(self):
        self.declist = []

    def append(self, node: DecNode):
        self.declist.append(node)

    def __str__(self):
        return f'{self.__class__.__name__}(\n' + '    '*3 + \
            ('\n'+3*'    ').join(map(str, self.declist)) + ' )'

    def accept(self, visitor):
        return visitor.visitDecListNode(self)


class IfStmtNode(StmtNode):

    def __init__(self, cond: ExpNode, ifbody: BlockNode, elsebody: BlockNode = None):
        self.cond = cond
        self.ifbody = ifbody
        self.elsebody = elsebody  # this can be None if this if stmt is not paired with a else statement

    def __str__(self):
        return f"{self.__class__.__name__}( IF ({self.cond}) {{ {self.ifbody} }} ELSE {{ {self.elsebody} }} )"

    def accept(self, visitor):
        return visitor.visitIfStmtNode(self)


class LoopNode(StmtNode):

    def __init__(self, pre: BlockNode, cond: ExpNode, body: BlockNode, post: BlockNode):
        self.pre, self.cond, self.body, self.post = pre, cond, body, post

    def __str__(self):
        return f"{self.__class__.__name__}( {self.pre} LOOP({self.cond}) {{ {self.body}\n{self.post} }} )"

    def accept(self, visitor):
        return visitor.visitLoopNode(self)


class BreakNode(StmtNode):
    pass


class ContinueNode(StmtNode):
    pass
