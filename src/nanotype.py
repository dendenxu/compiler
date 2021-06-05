from argparse import RawDescriptionHelpFormatter
from llvmlite import ir, binding
from nanoast import *

make_ptr = ir.PointerType
int32 = ir.IntType(32)
int1 = ir.IntType(1)
void = ir.VoidType()
flpt = ir.FloatType()
long = ir.IntType(64)

tp_visitor = None

def typ(node: Node):
    # print(tp_visitor)
    if type(node) == ParamNode:
        return typ(node.type)
    elif type(node) == IDNode:
        return tp_visitor._get_id_type(nam(node))
    elif isinstance(node, EmptyExpNode):
        return node.exp_type
    elif type(node) in (FloatNode, IntNode, TypeNode, FuncNode):
        return node.type
    elif type(Node) == ArrSubNode:
        print('here')
        return node.exp_type
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
    if type(node) in (IDNode, CallNode, IntNode, FloatNode, BinaryNode, UnaryNode, ArrSubNode):
        try:
            return node.value
        except AttributeError as e:
            node.value = tp_visitor._get_builder().load(node.ref)
            return node.value
    else:
        print(type(node))
        raise NotImplementedError

def exp_type(node: Node) -> str:
    try:
        return node.exp_type
    except AttributeError as e:
        try:
            node.exp_type = str(typ(node))
            return node.exp_type
        except Exception as e:
            print(node)
    except NotImplementedError as e:
        print(type(node))

binCompatDict = {
    #left       right      op       ret_type
    ('i32',     'i32',     '+' ):   'i32',
    ('i32',     'i32',     '-' ):   'i32',
    ('i32',     'i32',     '*' ):   'i32',
    ('i32',     'i32',     '/' ):   'i32',
    ('i32',     'i32',     '%' ):   'i32',
    ('i32',     'i32',     '!='):   'i1',
    ('i32',     'i32',     '=='):   'i1',
    ('i32',     'i32',     '<' ):   'i1',
    ('i32',     'i32',     '>' ):   'i1',
    ('i32',     'i32',     '<='):   'i1',
    ('i32',     'i32',     '>='):   'i1',
    ('i32',     'i32',     '||'):   'i1',
    ('i32',     'i32',     '&&'):   'i1',
    ('float',   'float',   '+' ):   'float',
    ('float',   'float',   '-' ):   'float',
    ('float',   'float',   '*' ):   'float',
    ('float',   'float',   '/' ):   'float',
    ('float',   'float',   '%' ):   'float',
    ('float',   'float',   '!='):   'i1',
    ('float',   'float',   '=='):   'i1',
    ('float',   'float',   '<' ):   'i1',
    ('float',   'float',   '>' ):   'i1',
    ('float',   'float',   '<='):   'i1',
    ('float',   'float',   '>='):   'i1',
    ('float',   'float',   '||'):   'i1',
    ('float',   'float',   '&&'):   'i1',
    ('i1',      'i1',      '+' ):   'i32',
    ('i1',      'i1',      '-' ):   'i32',
    ('i1',      'i1',      '*' ):   'i32',
    ('i1',      'i1',      '/' ):   'i32',
    ('i1',      'i1',      '%' ):   'i32',
    ('i1',      'i1',      '!='):   'i1',
    ('i1',      'i1',      '=='):   'i1',
    ('i1',      'i1',      '<' ):   'i1',
    ('i1',      'i1',      '>' ):   'i1',
    ('i1',      'i1',      '<='):   'i1',
    ('i1',      'i1',      '>='):   'i1',
    ('i1',      'i1',      '||'):   'i1',
    ('i1',      'i1',      '&&'):   'i1',
    ('i32',     'i1',      '+' ):   'i32',
    ('i32',     'i1',      '-' ):   'i32',
    ('i32',     'i1',      '*' ):   'i32',
    ('i32',     'i1',      '/' ):   'i32',
    ('i32',     'i1',      '%' ):   'i32',
    ('i32',     'i1',      '!='):   'i1',
    ('i32',     'i1',      '=='):   'i1',
    ('i32',     'i1',      '<' ):   'i1',
    ('i32',     'i1',      '>' ):   'i1',
    ('i32',     'i1',      '<='):   'i1',
    ('i32',     'i1',      '>='):   'i1',
    ('i32',     'i1',      '||'):   'i1',
    ('i32',     'i1',      '&&'):   'i1',
    ('i1',      'i32',     '+' ):   'i32',
    ('i1',      'i32',     '-' ):   'i32',
    ('i1',      'i32',     '*' ):   'i32',
    ('i1',      'i32',     '/' ):   'i32',
    ('i1',      'i32',     '%' ):   'i32',
    ('i1',      'i32',     '!='):   'i1',
    ('i1',      'i32',     '=='):   'i1',
    ('i1',      'i32',     '<' ):   'i1',
    ('i1',      'i32',     '>' ):   'i1',
    ('i1',      'i32',     '<='):   'i1',
    ('i1',      'i32',     '>='):   'i1',
    ('i1',      'i32',     '||'):   'i1',
    ('i1',      'i32',     '&&'):   'i1',
    ('float',   'i32',     '+' ):   'float',
    ('float',   'i32',     '-' ):   'float',
    ('float',   'i32',     '*' ):   'float',
    ('float',   'i32',     '/' ):   'float',
    ('float',   'i32',     '%' ):   'float',
    ('float',   'i32',     '!='):   'i1',
    ('float',   'i32',     '=='):   'i1',
    ('float',   'i32',     '<' ):   'i1',
    ('float',   'i32',     '>' ):   'i1',
    ('float',   'i32',     '<='):   'i1',
    ('float',   'i32',     '>='):   'i1',
    ('float',   'i32',     '||'):   'i1',
    ('float',   'i32',     '&&'):   'i1',
    ('i32',     'float',   '+' ):   'float',
    ('i32',     'float',   '-' ):   'float',
    ('i32',     'float',   '*' ):   'float',
    ('i32',     'float',   '/' ):   'float',
    ('i32',     'float',   '%' ):   'float',
    ('i32',     'float',   '!='):   'i1',
    ('i32',     'float',   '=='):   'i1',
    ('i32',     'float',   '<' ):   'i1',
    ('i32',     'float',   '>' ):   'i1',
    ('i32',     'float',   '<='):   'i1',
    ('i32',     'float',   '>='):   'i1',
    ('i32',     'float',   '||'):   'i1',
    ('i32',     'float',   '&&'):   'i1',
    ('i1',      'float',   '+' ):   'float',
    ('i1',      'float',   '-' ):   'float',
    ('i1',      'float',   '*' ):   'float',
    ('i1',      'float',   '/' ):   'float',
    ('i1',      'float',   '%' ):   'float',
    ('i1',      'float',   '!='):   'i1',
    ('i1',      'float',   '=='):   'i1',
    ('i1',      'float',   '<' ):   'i1',
    ('i1',      'float',   '>' ):   'i1',
    ('i1',      'float',   '<='):   'i1',
    ('i1',      'float',   '>='):   'i1',
    ('i1',      'float',   '||'):   'i1',
    ('i1',      'float',   '&&'):   'i1',
    ('float',   'i1',      '+' ):   'float',
    ('float',   'i1',      '-' ):   'float',
    ('float',   'i1',      '*' ):   'float',
    ('float',   'i1',      '/' ):   'float',
    ('float',   'i1',      '%' ):   'float',
    ('float',   'i1',      '!='):   'i1',
    ('float',   'i1',      '=='):   'i1',
    ('float',   'i1',      '<' ):   'i1',
    ('float',   'i1',      '>' ):   'i1',
    ('float',   'i1',      '<='):   'i1',
    ('float',   'i1',      '>='):   'i1',
    ('float',   'i1',      '||'):   'i1',
    ('float',   'i1',      '&&'):   'i1',
}

def binCompat(left: Node, right: Node, op: str):
    if not ((exp_type(left), exp_type(right), op) in binCompatDict.keys()):
        if exp_type(left) != exp_type(right):
            print(exp_type(left), exp_type(right))
            print(left, right)
            raise RuntimeError("type mismatch")
        ret_type = exp_type(left)
    else:
        ret_type = binCompatDict[exp_type(left),exp_type(right),op]
        
    if exp_type(left) == 'i1' and exp_type(right) == 'i1' and op in ('+','-','*','/','%'):
        left.value = tp_visitor._get_builder().zext(val(left), int32)
        right.value = tp_visitor._get_builder().zext(val(right), int32)
    elif exp_type(left) == 'i1' and exp_type(right) == 'i32':
        left.value = tp_visitor._get_builder().zext(val(left), int32)
    elif exp_type(left) == 'i32' and exp_type(right) == 'i1':
        right.value = tp_visitor._get_builder().zext(val(right), int32)
    elif exp_type(left) == 'i32' and exp_type(right) == 'float':
        left.value = tp_visitor._get_builder().sitofp(val(left), flpt)
    elif exp_type(left) == 'float' and exp_type(right) == 'i32':
        right.value = tp_visitor._get_builder().sitofp(val(right), flpt)
    elif exp_type(left) == 'i1' and exp_type(right) == 'float':
        left.value = tp_visitor._get_builder().uitofp(val(left), flpt)
    elif type(left) == 'float' and type(right) == 'i1':
        right.value = tp_visitor._get_builder().uitofp(val(right), flpt)
    
    if op in ('||', '&&'):
        if exp_type(left) == 'i32':
            left.value = tp_visitor._get_builder().icmp_signed('!=', val(left), ir.Constant(int32, 0))
        elif exp_type(left) == 'float':
            left.value = tp_visitor._get_builder().fcmp_ordered('!=', val(left), ir.Constant(flpt, 0))
            
        if exp_type(right) == 'i32':
            right.value = tp_visitor._get_builder().icmp_signed('!=', val(right), ir.Constant(int32, 0))
        elif exp_type(right) == 'float':
            right.value = tp_visitor._get_builder().fcmp_ordered('!=', val(right), ir.Constant(flpt, 0))
    
    return ret_type

allowed_casting = [
    ('i1'    , 'i32'  ),
    ('i32'   , 'float'),
    ('i1'    , 'float'),
    ('float' , 'i1'   ),
    ('float' , 'i32'  )   
]

def cast(value, tgt_type: str):
    src_type = str(value.type)
    if not ((src_type, tgt_type) in allowed_casting):
        raise RuntimeError("unable to cast from %s to %s"%(src_type, tgt_type))
    if (src_type, tgt_type) == ('i1', 'i32'):
        return tp_visitor._get_builder().zext(value, int32)
    elif (src_type, tgt_type) == ('i32', 'float'):
        return tp_visitor._get_builder().sitofp(value, flpt)
    elif (src_type, tgt_type) == ('i1', 'float'):
        return tp_visitor._get_builder().uitofp(value, flpt)
    elif (src_type, tgt_type) == ('float', 'i32'):
        return tp_visitor._get_builder().fptosi(value, int32)
    elif (src_type, tgt_type) == ('float', 'i1'):
        return tp_visitor._get_builder().fptoui(value, int1)