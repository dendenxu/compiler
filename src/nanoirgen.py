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
        # we do not need list since we only support single file compiling
        self.cur_ll_module = None
        # we do not need list since we do not support sub-procedure
        self.cur_func_name = ''
        self.block_stack = []
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

    def _push_block(self, block=None):
        func = self.defined_funcs[self.cur_func_name]
        if block is None:
            block = func.append_basic_block()
        self.block_stack.append(ir.IRBuilder(block))

    def _get_block(self):
        return self.block_stack[-1]
    
    def _pop_block(self):
        self.block_stack.pop()

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
        # scope for global variables
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
        # backup old function name
        old_func_name = self.cur_func_name
        self.cur_func_name = node.id.name
        self._add_func(node.id.name, node.ll_func)
        self._push_block()
        node.block.accept(self)
        self._pop_block()
        self.cur_func_name = old_func_name

    def visitTypeNode(self, node: TypeNode):
        if node.typestr == 'int':
            node.ll_type = ir.IntType(32)

    def visitBlockNode(self, node: BlockNode):
        self._push_scope()
        for stmt in node.stmts:
            stmt.accept(self)
        self._pop_scope()

    def visitRetNode(self, node: RetNode):
        node.exp.accept(self)
        self._get_block().ret(node.exp.ll_value)

    def visitIDNode(self, node: IDNode):
        item = self._get_identifier(node.name)
        if item is None:
            raise RuntimeError(node.name, "not declared")
        node.ll_value = self._get_block().load(item)

    def visitIntNode(self, node: IntNode):
        node.ll_value = int32(node.value)

    def visitPrimNode(self, node: BinopNode):
        node.node.accept(self)
        node.ll_value = node.node.ll_value

    def visitUnaryNode(self, node: UnaryNode):
        node.node.accept(self)
        if node.op == '+':
            node.ll_value = node.node.ll_value
        elif node.op == '-':
            node.ll_value = self._get_block().mul(node.node.ll_value, int32(-1))
        elif node.op == '!':
            node.ll_value = self._get_block().icmp_signed('==', node.node.ll_value, int32(0))
        elif node.op == '~':
            node.ll_value = self._get_block().not_(node.node.ll_value)

    def visitDecNode(self, node: DecNode):
        node.item = self._get_block().alloca(int32, name=node.id.name)
        if node.init is not None:
            node.init.accept(self)
            self._get_block().store(node.init.ll_value, node.item)
        self._add_identifier(node.id.name, node.item)

    def visitAssNode(self, node: AssNode):
        item = self._get_identifier(node.id.name)
        if item is None:
            raise RuntimeError(node.id.name, "not declared")
        node.exp.accept(self)
        self._get_block().store(node.exp.ll_value, item)

    def visitIfStmtNode(self, node: IfStmtNode):
        node.cond.accept(self)
        pred = self._get_block().icmp_signed('!=', node.cond.ll_value, int32(0))
        if type(node.ifbody) == StmtNode:
            return
        if type(node.elsebody) == StmtNode:
            with self._get_block().if_then(pred) as then:
                self._push_block(then)
                self._push_scope()
                node.ifbody.accept(self)
                self._pop_scope()
                self._pop_block()
        else:
            with self._get_block().if_else(pred) as (then, othrewise):
                # print('========debug========\n',then)
                with then:
                    # ifbody
                    self._push_scope()
                    node.ifbody.accept(self)
                    self._pop_scope()
                with othrewise:
                    # elsebody
                    self._push_scope()
                    node.elsebody.accept(self)
                    self._pop_scope()
                
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
        
        for:
            pre: StmtNode / DecNode
            cond: ExpNode / subclass of ExpNode / LiteralNode / IDNode
            body: BlockNode
            post: ExpNode / subclass of ExpNode / LiteralNode / IDNode
        while:
            pre: StmtNode
            cond: ExpNode / subclass of ExpNode / LiteralNode / IDNode
            body: BlockNode
            post: StmtNode
        do-while:
            pre: BlockNode
            cond: 'while'
            body: ExpNode / subclass of ExpNode / LiteralNode / IDNode
            post: StmtNode()
        """
        # scope_new_0

        print('node.pre', node.pre)
        print('node.cond', node.cond)
        print('node.body', node.body)
        print('node.post', node.post)

    def visitBinopNode(self, node: BinopNode):
        node.left.accept(self)
        node.right.accept(self)
        if node.op == '+':
            node.ll_value = self._get_block().add(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '-':
            node.ll_value = self._get_block().sub(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '*':
            node.ll_value = self._get_block().mul(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '/':
            node.ll_value = self._get_block().sdiv(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '%':
            node.ll_value = self._get_block().srem(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '<':
            node.ll_value = self._get_block().icmp_signed(
                '<',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '>':
            node.ll_value = self._get_block().icmp_signed(
                '<',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '==':
            node.ll_value = self._get_block().icmp_signed(
                '==',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '!=':
            node.ll_value = self._get_block().icmp_signed(
                '!=',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '<=':
            node.ll_value = self._get_block().icmp_signed(
                '<=',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '>=':
            node.ll_value = self._get_block().icmp_signed(
                '>=',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '>':
            node.ll_value = self._get_block().icmp_signed(
                '>',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '||':
            explicit_value = self._get_block().or_(
                node.left.ll_value,
                node.right.ll_value)
            bit_1_value = self._get_block().icmp_signed(
                '!=',
                explicit_value,
                int32(0))
            node.ll_value = self._get_block().zext(
                bit_1_value,
                int32)
        elif node.op == '&&':
            explicit_value = self._get_block().and_(
                node.left.ll_value,
                node.right.ll_value)
            bit_1_value = self._get_block().icmp_signed(
                '!=',
                explicit_value,
                int32(0))
            node.ll_value = self._get_block().zext(
                bit_1_value,
                int32)


if __name__ == '__main__':
    with open('../samples/fx.c', 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        lexer.build()
        parser = NanoParser()
        parser.build()
        root = parser.parse(content, lexer=lexer)
        print(root)
        visitor = NanoVisitor()
        visitor.visitProgNode(root)
        ir = str(root.ll_module).replace('unknown-unknown-unknown',
                                         'x86_64-pc-linux')
        print(f"{ir}")
    with open('../results/irgen.ll', 'w') as I:
        I.write(ir)
