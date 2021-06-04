from llvmlite.ir import builder
from llvmlite.ir.instructions import ICMPInstr
from ply import yacc
from nanoast import *
from nanolex import NanoLexer
from nanoyacc import NanoParser
from nanotype import *
import sys
from termcolor import colored
from llvmlite import ir, binding
import copy

class Visitor:
    pass


class NanoVisitor(Visitor):
    def __init__(self):
        self.result_dict = {}  # Node -> int
        self.cur_ll_module = None # single file
        self.cur_ll_block_builders = []
        self.cur_func_name = '' # do not support sub_function
        self.scope_stack = []
        self.defined_funcs = dict()
    
    def _push_scope(self):
        if len(self.scope_stack) == 0:
            self.scope_stack.append(dict())
        else:
            dic = copy.deepcopy(self.scope_stack[-1])
            self.scope_stack.append(dic)
    def _pop_scope(self):
        self.scope_stack.pop()
    def _add_identifier(self, name, item):
        if name in self.scope_stack[-1].keys():
            raise RuntimeError("{name} alredy declared")
        self.scope_stack[-1][name] = item
    def _get_identifier(self, name):
        if name in self.scope_stack[-1].keys():
            return self.scope_stack[-1][name]
        else:
            return None
    def _add_func(self, name, func):
        if name in self.defined_funcs.keys():
            raise RuntimeError("{name} alredy declared")
        self.defined_funcs[name] = func
    def _get_func(self, name):
        if name in self.defined_funcs.keys():
            return self.defined_funcs[name]
        else:
            return None
    
    def visitProgNode(self, node: ProgNode):
        self._push_scope()
        node.ll_module = ir.Module(name='program')
        self.ll_module = node.ll_module
        for func in node.funcs:
            func.accept(self)
        self._pop_scope()
        
    def visitFuncNode(self, node: FuncNode):
        node.type.accept(self)
        node.ll_func_type = ir.FunctionType(node.type.ll_type, ())
        node.ll_func = ir.Function(self.ll_module, node.ll_func_type, name=node.id.name)
        old_func_name = self.cur_func_name
        self.cur_func_name = node.id.name
        self._add_func(node.id.name, node.ll_func)
        node.block.accept(self)
        self.cur_func_name = old_func_name
        
    def visitTypeNode(self, node: TypeNode):
        if node.typestr == 'int':
            node.ll_type = ir.IntType(32)
        
    def visitBlockNode(self, node: BlockNode):
        self._push_scope()
        cur_ll_func = self.defined_funcs[self.cur_func_name]
        ll_block = cur_ll_func.append_basic_block()
        ll_builder = ir.IRBuilder(ll_block)
        self.cur_ll_block_builders.append(ll_builder)
        for stmt in node.stmts:
            stmt.accept(self)
        self.cur_ll_block_builders.pop()
        self._pop_scope()
            
    def visitRetNode(self, node: RetNode):
        print(self.ll_module)
        node.exp.accept(self)
        self.cur_ll_block_builders[-1].ret(node.exp.ll_value)
    
    def visitIDNode(self, node: IDNode):
        item = self._get_identifier(node.name)
        if item is None:
            raise RuntimeError(node.left.name, "not declared")
        node.ll_value = self.cur_ll_block_builders[-1].load(item)
        
    def visitIntNode(self, node: IntNode):
        node.ll_value = int32(node.value)

    def visitPrimNode(self, node: BinopNode):
        node.node.accept(self)
        node.ll_value = node.node.ll_value
    
    def visitDecNode(self, node: DecNode):
        node.item = self.cur_ll_block_builders[-1].alloca(int32, name=node.id.name)
        if node.init is not None:
            node.init.accept(self)
            self.cur_ll_block_builders[-1].store(node.init.ll_value, node.item)
        self._add_identifier(node.id.name, node.item)

    def visitDecListNode(self, node: DecListNode):
        for dec in node.declist:
            dec.accept(self)
        
    def visitAssNode(self, node: AssNode):
        item = self._get_identifier(node.id.name)
        if item is None:
            raise RuntimeError(node.id.name, "not declared")
        node.exp.accept(self)
        self.cur_ll_block_builders[-1].store(node.exp.ll_value, item)
    
    def visitIfStmtNode(self, node: IfStmtNode):
        node.cond.accept(self)
        pred = self.cur_ll_block_builders[-1].icmp_signed('!=', node.cond.ll_value, int32(0))
        print('here', self.cur_ll_block_builders)
        if type(node.elsebody) == StmtNode:
            with self.cur_ll_block_builders[-1].if_then(pred) as then:
                # self._push_scope()
                # cur_ll_func = self.defined_funcs[self.cur_func_name]
                # ll_block = cur_ll_func.append_basic_block()
                # ll_builder = ir.IRBuilder(ll_block)
                # self.cur_ll_block_builders.append(ll_builder)
                node.ifbody.accept(self)
                # self.cur_ll_block_builders.pop()
                # self._pop_scope()
            # with otherwise:
            #     if type(node.elsebody) != StmtNode:
            #         self._push_scope()
            #         cur_ll_func = self.defined_funcs[self.cur_func_name]
            #         ll_block = cur_ll_func.append_basic_block()
            #         ll_builder = ir.IRBuilder(ll_block)
            #         self.cur_ll_block_builders.append(ll_builder)
            #         node.elsebody.accept(self)
            #         self._pop_scope()
    
    def visitLoopNode(self, node: LoopNode):
        """
                ...scope_original...
        /======================scope_new_0===/
        /  pre -> cond <----|                /
        /  /=========|======|==scope_new_1===/
        /  /        body    |                /
        /  /=========|======|==scope_new_2===/
        /           post----|                /
        /====================================/
        """
        # 
        self._push_scope()
        cur_ll_func = self.defined_funcs[self.cur_func_name]
        ll_block = cur_ll_func.append_basic_block()
        ll_builder = ir.IRBuilder(ll_block)
        self.cur_ll_block_builders.append(ll_builder)

        

        self._pop_scope()
    
    def visitBinopNode(self, node: BinopNode):
        node.left.accept(self)
        node.right.accept(self)
        if node.op == '+':
            node.ll_value = self.cur_ll_block_builders[-1].add(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '-':
            node.ll_value = self.cur_ll_block_builders[-1].sub(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '*':
            node.ll_value = self.cur_ll_block_builders[-1].mul(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '/':
            node.ll_value = self.cur_ll_block_builders[-1].sdiv(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '%':
            node.ll_value = self.cur_ll_block_builders[-1].srem(
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '<':
            node.ll_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '<',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '>':
            node.ll_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '<',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '==':
            node.ll_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '==',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '!=':
            node.ll_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '!=',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '<=':
            node.ll_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '<=',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '>=':
            node.ll_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '>=',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '>':
            node.ll_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '>',
                                node.left.ll_value,
                                node.right.ll_value)
        elif node.op == '||':
            explicit_value = self.cur_ll_block_builders[-1].or_(
                                node.left.ll_value,
                                node.right.ll_value)
            bit_1_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '!=',
                                explicit_value,
                                int32(0))
            node.ll_value = self.cur_ll_block_builders[-1].zext(
                                bit_1_value,
                                int32)
        elif node.op == '&&':
            explicit_value = self.cur_ll_block_builders[-1].and_(
                                node.left.ll_value,
                                node.right.ll_value)
            bit_1_value = self.cur_ll_block_builders[-1].icmp_signed(
                                '!=',
                                explicit_value,
                                int32(0))
            node.ll_value = self.cur_ll_block_builders[-1].zext(
                                bit_1_value,
                                int32)


if __name__ == '__main__':
    with open('../samples/fx.c', 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        lexer.build()
        parser = NanoParser()
        parser.build()
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



