from llvmlite.ir import builder
from ply import yacc
from nanoast import *
from nanolex import NanoLexer
from nanoyacc import NanoParser
from nanotype import *
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
    
    def visitProgNode(self, node: ProgNode):
        node.ll_module = ir.Module(name='program')
        self.ll_module = node.ll_module
        node.func.accept(self)
        
    def visitFuncNode(self, node: FuncNode):
        node.type.accept(self)
        node.ll_func_type = ir.FunctionType(node.type.ll_type, ())
        node.ll_func = ir.Function(self.ll_module, node.ll_func_type, name=node.id)
        self.ll_cur_func.append(node.ll_func)
        node.block.accept(self)
        self.ll_cur_func.pop()
        
    def visitTypeNode(self, node: TypeNode):
        node.ll_type = ir.IntType(32)
        
    def visitBlockNode(self, node: BlockNode):
        for stmt in node.stmts:
            ll_block = self.ll_cur_func[-1].append_basic_block()
            ll_builder = ir.IRBuilder(ll_block)
            self.ll_cur_block_builder.append(ll_builder)
            stmt.accept(self)
            self.ll_cur_block_builder.pop()
            
    def visitRetNode(self, node: RetNode):
        node.exp.accept(self)
        self.ll_cur_block_builder[-1].ret(node.exp.ll_value)
        
    def visitIntNode(self, node: IntNode):
        node.ll_value = int32(node.value)

    def visitPrimNode(self, node: BinopNode):
        node.node.accept(self)
        node.ll_value = node.node.ll_value
    
    def visitDecNode(self, node: DecNode):
        node.item = self.ll_cur_block_builder[-1].alloca(int32, name=node.id)
        
    def visitAssNode(self, node: AssNode):
        pass

    def visitBinopNode(self, node: BinopNode):
        node.left.accept(self)
        node.right.accept(self)
        if node.op == '+':
            node.ll_value = self.ll_cur_block_builder[-1].add(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '-':
            node.ll_value = self.ll_cur_block_builder[-1].sub(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '*':
            node.ll_value = self.ll_cur_block_builder[-1].mul(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '/':
            node.ll_value = self.ll_cur_block_builder[-1].sdiv(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '%':
            node.ll_value = self.ll_cur_block_builder[-1].srem(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '<':
            node.ll_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '<',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '>':
            node.ll_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '<',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '==':
            node.ll_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '==',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '!=':
            node.ll_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '!=',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '<=':
            node.ll_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '<=',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '>=':
            node.ll_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '>=',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '>':
            node.ll_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '>',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '||':
            explicit_value = self.ll_cur_block_builder[-1].or_(
                                node.left.ll_value,
                                node.right.ll_value)
            bit_1_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '!=',
                                explicit_value,
                                int32(0))
            node.ll_value = self.ll_cur_block_builder[-1].zext(
                                bit_1_value,
                                int32)
        elif node.op == '&&':
            explicit_value = self.ll_cur_block_builder[-1].and_(
                                node.left.ll_value,
                                node.right.ll_value)
            bit_1_value = self.ll_cur_block_builder[-1].icmp_signed(
                                '!=',
                                explicit_value,
                                int32(0))
            node.ll_value = self.ll_cur_block_builder[-1].zext(
                                bit_1_value,
                                int32)


if __name__ == '__main__':
    with open('../samples/fx.c', 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        parser = NanoParser()
        visitor = NanoVisitor()
        root = parser.parse(content, lexer=lexer)
        print(root)
        visitor = NanoVisitor()
        visitor.visitProgNode(root)
        ir = str(root.ll_module).replace('unknown-unknown-unknown',
                                         'x86_64-pc-linux')
        print(f"{ir}")
    with open('../results/irgen.ll', 'w') as I:
        I.write(ir)



