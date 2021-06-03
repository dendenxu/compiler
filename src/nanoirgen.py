from llvmlite.ir import builder
from ply import yacc
from nanoast import *
from nanolex import NanoLexer
from nanoyacc import NanoParser
import sys
from termcolor import colored
from llvmlite import ir, binding

class Visitor:
    pass


class NanoVisitor(Visitor):
    def __init__(self):
        self.result_dict = {}  # Node -> int
        
    def cache_result(visit):  # decorator
        def wrapped(self, node, father=None):
            if node in self.result_dict:
                return self.result_dict[node]
            value = visit(self, node, father)
            # print(f"Getting: {value}({type(value)})")
            self.result_dict[node] = value
            return value
        return wrapped
    
    @cache_result
    def visitProgNode(self, node: ProgNode, father=None):
        node.ll_module = ir.Module(name='program')
        node.func.accept(self, node)
        
    @cache_result
    def visitFuncNode(self, node: FuncNode, father=None):
        node.type.accept(self, node)
        node.ll_type = ir.FunctionType(node.type.ll_type, ())
        node.ll_func = ir.Function(father.ll_module, node.ll_type, name=node.id)
        node.block.accept(self, node)
        
    @cache_result
    def visitTypeNode(self, node: TypeNode, father=None):
        node.ll_type = ir.IntType(32)
        
    @cache_result
    def visitBlockNode(self, node: BlockNode, father=None):
        node.ll_type = father.ll_type
        node.ll_func = father.ll_func
        for stmt in node.stmts:
            stmt.accept(self, node)
            
    @cache_result
    def visitRetNode(self, node: RetNode, father=None):
        node.ll_block = father.ll_func.append_basic_block()
        node.ll_builder = ir.IRBuilder(node.ll_block)
        node.exp.accept(self, node)
        node.ll_builder.ret(node.exp.ll_value)
        
    @cache_result
    def visitIntNode(self, node: IntNode, father=None):
        int32 = ir.IntType(32)
        node.ll_value = int32(node.value)
        
    @cache_result
    def visitBinopNode(self, node: BinopNode, father=None):
        if node.op is '+':
            node.left.accept(self, node)
            node.right.accept(self, node)
            node.ll_value = father.ll_builder.add(
                                node.left.ll_value,
                                node.right.ll_value)
    


if __name__ == '__main__':
    with open('../samples/fx.c', 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        parser = NanoParser()
        visitor = NanoVisitor()
        root = parser.parse(content, lexer=lexer)
        # print(root)
        visitor = NanoVisitor()
        visitor.visitProgNode(root)
        print(f"Result: {root.ll_module}")
    with open('../results/irgen.ll', 'w') as I:
        I.write(str(root.ll_module))
    
    """
    type_int = ir.IntType(32)
    functype__int__void = ir.FunctionType(type_int, ())
    module = ir.Module(name="for_test")
    func = ir.Function(module, functype__int__void, name="main")
    block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    builder.ret(ir.Constant(type_int, 0))
    print(module)
    """



