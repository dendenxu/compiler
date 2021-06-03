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
        self.ll_module = None
        self.ll_cur_func = []
        self.ll_cur_block_builder = []
        
    def cache_result(visit):  # decorator
        def wrapped(self, node):
            if node in self.result_dict:
                return self.result_dict[node]
            value = visit(self, node)
            # print(f"Getting: {value}({type(value)})")
            self.result_dict[node] = value
            return value
        return wrapped
    
    @cache_result
    def visitProgNode(self, node: ProgNode):
        node.ll_module = ir.Module(name='program')
        self.ll_module = node.ll_module
        node.func.accept(self)
        
    @cache_result
    def visitFuncNode(self, node: FuncNode):
        node.type.accept(self)
        node.ll_func_type = ir.FunctionType(node.type.ll_type, ())
        node.ll_func = ir.Function(self.ll_module, node.ll_func_type, name=node.id)
        self.ll_cur_func.append(node.ll_func)
        node.block.accept(self)
        self.ll_cur_func.pop()
        
    @cache_result
    def visitTypeNode(self, node: TypeNode):
        node.ll_type = ir.IntType(32)
        
    @cache_result
    def visitBlockNode(self, node: BlockNode):
        for stmt in node.stmts:
            stmt.accept(self)
            
    @cache_result
    def visitRetNode(self, node: RetNode):
        node.ll_block = self.ll_cur_func[-1].append_basic_block()
        node.ll_builder = ir.IRBuilder(node.ll_block)
        self.ll_cur_block_builder.append(node.ll_builder)
        node.exp.accept(self)
        node.ll_builder.ret(node.exp.ll_value)
        self.ll_cur_block_builder.pop()
        
    @cache_result
    def visitIntNode(self, node: IntNode):
        int32 = ir.IntType(32)
        node.ll_value = int32(node.value)
        
    @cache_result
    def visitBinopNode(self, node: BinopNode):
        node.left.accept(self)
        node.right.accept(self)
        if node.op is '+':
            node.ll_value = self.ll_cur_block_builder[-1].add(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op is '-':
            node.ll_value = self.ll_cur_block_builder[-1].sub(
                                node.left.ll_value,
                                node.right.ll_value)
    
    @cache_result
    def visitPrimNode(self, node: BinopNode):
        node.node.accept(self)
        node.ll_value = node.node.ll_value
    


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



