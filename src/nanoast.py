from typing import List

class Node(object):
    # A simple Abstract Syntax Tree node
    def accept(self, visitor):
        pass


# class ProgramNode(Node):
#     def __init__(self, left: Node, right: Node):
#         self.left, self.right = left, right

# class TypeNode(Node):
#     def __init__(self, type, literal: str, typetype):
#         self.type, self.literal, self.typetype = type, literal, typetype

# class TypeIDNode(Node):
#     def __init__(self, type: TypeNode, id: str):
#         self.type, self.id = type, id

# class ParamListNode(Node):
#     def __init__(self, typeids: List(TypeIDNode)):
#         self.typeids = typeids

# class BlockNode(Node):
#     pass

# class DecNode(BlockNode):
#     def __init__(self):
#         pass

# class StmtNode(Node):
#     def __init__(self):
#         pass

# class FunctionNode(Node):
#     def __init__(self, type: TypeNode, id: str, params: ParamListNode, blocks: List(BlockNode)):
#         self.type, self.id, self.params, self.blocks = type, id, params, blocks



class IntNode(Node):
    def __init__(self, value: int):
        self.value = value

    def __str__(self):
        return f"({self.value})"

    def accept(self, visitor):
        return visitor.visitIntNode(self)


class BinopNode(Node):
    _legal_ops = {*"+-*/%"}

    def __init__(self, op: str, left: Node, right: Node):
        assert op in BinopNode._legal_ops
        self.op, self.left, self.right = op, left, right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

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
