from llvmlite import ir, binding
from nanoast import *

make_ptr = ir.PointerType
int32 = ir.IntType(32)
bool = ir.IntType(1)
int1 = ir.IntType(1)

def typ(node: Node):
    if type(node) == ParamNode:
        return typ(node.type)
    elif type(node) == TypeNode:
        return node.type
    elif type(node) == FuncNode:
        return node.type
    else:
        print(type(node))
        raise NotImplementedError

def nam(node: Node):
    if type(node) == IDNode:
        return node.name
    elif type(node) == ParamNode:
        return nam(node.id)
    elif type(node) == FuncNode:
        return nam(node.id)
    elif type(node) == CallNode:
        return nam(node.id)
    else:
        print(type(node))
        raise NotImplementedError

def ref(node: Node):
    if type(node) == FuncNode:
        return node.ref
    elif type(node) == IDNode:
        return node.ref
    elif type(node) == UnaryNode:
        return node.ref
    elif type(node) == ArrSubNode:
        return node.ref
    else:
        print(type(node))
        raise NotImplementedError

def val(node: Node):
    if type(node) == IDNode:
        return node.value
    elif type(node) == CallNode:
        return node.value
    elif type(node) == IntNode:
        return node.value
    elif type(node) == BinaryNode:
        return node.value
    elif type(node) == UnaryNode:
        return node.value
    elif type(node) == ArrSubNode:
        return node.value
    else:
        print(type(node))
        raise NotImplementedError
        