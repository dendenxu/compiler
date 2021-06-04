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
        # we do not need list since we only support single filre compiling
        self.cur_ll_module = None
        # we do not need list since we do not support sub-procedure
        self.cur_func_name = ''
        self.builder_stack = []
        self.block_stack = []
        self.scope_stack = []
        self.defined_funcs = dict()
        self.func_params = dict()

    def _push_builder(self, builder=None):
        if builder is not None:
            self.builder_stack.append(builder)
        else:
            block = self._get_block()
            builder = ir.IRBuilder(block)
            self.builder_stack.append(builder)

    def _get_builder(self):
        return self.builder_stack[-1]

    def _pop_builder(self):
        return self.builder_stack.pop()

    def _push_scope(self):
        self.scope_stack.append(dict())

    def _pop_scope(self):
        return self.scope_stack.pop()

    def _push_block(self, block=None):
        func = self._get_func(self.cur_func_name)
        if block is None:
            block = func.append_basic_block()
        self.block_stack.append(block)

    def _get_block(self):
        return self.block_stack[-1]

    def _pop_block(self):
        return self.block_stack.pop()

    def _add_identifier(self, name, item):
        if name in self.scope_stack[-1]:
            raise RuntimeError("{name} alredy declared")
        self.scope_stack[-1][name] = item

    def _get_identifier(self, name):
        for d in self.scope_stack[::-1]:  # reversing the scope_block
            if name in d:
                return d[name]
        return None

    def _add_func(self, name, func, params=dict()):
        if name in self.defined_funcs.keys():
            raise RuntimeError("{name} alredy declared")
        self.defined_funcs[name] = [func, params]

    def _get_func(self, name):
        if name in self.defined_funcs.keys():
            return self.defined_funcs[name][0]
        else:
            return None
    
    def _get_func_param_refs(self, name):
        if name in self.defined_funcs.keys():
            return self.defined_funcs[name][1]
        else:
            return None

    def visitProgNode(self, node: ProgNode):
        node.ll_module = ir.Module(name='program')
        self.ll_module = node.ll_module
        for func in node.funcs:
            func.accept(self)

    def visitFuncNode(self, node: FuncNode):
        self._push_scope()
    
        func_param_type_list = []
        for param in node.params:
            param.accept(self)
            func_param_type_list.append(param.type.ll_type)

        node.type.accept(self)
        ll_func_type = ir.FunctionType(node.type.ll_type, tuple(func_param_type_list))
        node.ll_func = ir.Function(self.ll_module, ll_func_type, name=node.id.name)
        self.cur_func_name = node.id.name
        self._add_func(node.id.name, node.ll_func)

        self._push_block()
        self._push_builder()
        
        func_args = list(node.ll_func.args)
        for i in range(len(func_args)):
            arg_ref = self._get_builder().alloca(func_param_type_list[i])
            self._add_identifier(node.params[i].id.name, arg_ref)
            self._get_builder().store(func_args[i], arg_ref)
        
        node.block.accept(self)
        
        self._pop_builder()
        self._pop_block()
        self._pop_scope()

    def visitCallNode(self, node: CallNode):
        call_func_args = []
        for param in node.params:
            param.accept(self)
            call_func_args.append(param.ll_value)
        func = self._get_func(node.id.name)
        node.ll_value = self._get_builder().call(func, tuple(call_func_args))

    def visitParamNode(self, node: ParamNode):
        node.type.accept(self)

    def visitTypeNode(self, node: TypeNode):
        if node.typestr == 'int':
            node.ll_type = ir.IntType(32)

    def visitBlockNode(self, node: BlockNode):
        self._push_scope()
        for stmt in node.stmts:
            stmt.accept(self)
        return self._pop_scope()

    def visitRetNode(self, node: RetNode):
        node.exp.accept(self)
        self._get_builder().ret(node.exp.ll_value)

    def visitIDNode(self, node: IDNode):
        item = self._get_identifier(node.name)
        if item is None:
            raise RuntimeError(node.name, "not declared")
        node.ll_value = self._get_builder().load(item)

    def visitIntNode(self, node: IntNode):
        node.ll_value = int32(node.value)

    def visitPrimNode(self, node: BinaryNode):
        node.node.accept(self)
        node.ll_value = node.node.ll_value

    def visitUnaryNode(self, node: UnaryNode):
        node.node.accept(self)
        if node.op == '+':
            node.ll_value = node.node.ll_value
        elif node.op == '-':
            node.ll_value = self._get_builder().mul(node.node.ll_value, int32(-1))
        elif node.op == '!':
            node.ll_value = self._get_builder().icmp_signed('==', node.node.ll_value, int32(0))
        elif node.op == '~':
            node.ll_value = self._get_builder().not_(node.node.ll_value)
        elif node.op == '*':
            raise NotImplementedError
        elif node.op == '&':
            raise NotImplementedError

    def visitDecNode(self, node: DecNode):
        node.item = self._get_builder().alloca(int32)
        if node.init is not None:
            node.init.accept(self)
            self._get_builder().store(node.init.ll_value, node.item)
        self._add_identifier(node.id.name, node.item)

    def visitAssNode(self, node: AssNode):
        item = self._get_identifier(node.id.name)
        if item is None:
            raise RuntimeError(node.id.name, "not declared")
        node.exp.accept(self)
        self._get_builder().store(node.exp.ll_value, item)

    def visitIfStmtNode(self, node: IfStmtNode):
        node.cond.accept(self)
        pred = self._get_builder().icmp_signed('!=', node.cond.ll_value, int32(0))
        if type(node.ifbody) == EmptyStmtNode:
            return
        if type(node.elsebody) == EmptyStmtNode:
            with self._get_builder().if_then(pred) as then:
                self._push_block(then)
                self._push_scope()
                node.ifbody.accept(self)
                self._pop_scope()
                self._pop_block()
        else:
            with self._get_builder().if_else(pred) as (then, othrewise):
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
        /  /=========|======|================/
        /           post----|                /
        /====================================/

        for:
            pre: EmptyStmtNode / DecNode
            cond: EmptyExpNode / subclass of EmptyExpNode / subclass of EmptyLiteralNode / IDNode
            body: BlockNode
            post: EmptyExpNode / subclass of EmptyExpNode / subclass of EmptyLiteralNode / IDNode
        while:
            pre: EmptyStmtNode
            cond: EmptyExpNode / subclass of EmptyExpNode / subclass of EmptyLiteralNode / IDNode
            body: BlockNode
            post: EmptyStmtNode
        do-while:
            pre: EmptyStmtNode()
            cond: EmptyExpNode / subclass of EmptyExpNode / subclass of EmptyLiteralNode / IDNode
            body: BlockNode()
            post: EmptyStmtNode()
        """

        print('pre', node.pre)
        print('cond', node.cond)
        print('body', node.body)
        print('post', node.post)

        # do-while
        if node.cond == 'while':
            node.cond = node.body
            node.body = node.pre
            node.pre = node.post
            
            # scope_new_0
            self._push_scope()
            body_block = self._get_builder().append_basic_block()
            post_block = self._get_builder().append_basic_block()
            self._get_builder().branch(body_block)
            self._get_builder().position_at_start(body_block)
            node.body.accept(self)
            node.cond.accept(self)
            cond = self._get_builder().icmp_signed('!=', node.cond.ll_value, int32(0))
            self._get_builder().cbranch(cond, body_block, post_block)
            self._get_builder().position_at_start(post_block)
            self._push_block(post_block)
            self._pop_scope()
        # while
        else:
            self._push_scope()
            if type(node.pre) != EmptyStmtNode:
                node.pre.accept(self)
            # scope_new_0
            if type(node.cond) != EmptyExpNode:
                node.cond.accept(self)
                cond = self._get_builder().icmp_signed('!=', node.cond.ll_value, int32(0))
            else:
                cond = bool(1)
            body_block = self._get_builder().append_basic_block()
            post_block = self._get_builder().append_basic_block()
            self._get_builder().cbranch(cond, body_block, post_block)

            # scope_new_1 auto created when visitBlockNode
            self._get_builder().position_at_start(body_block)
            node.body.accept(self)
            if type(node.post) != EmptyStmtNode:
                node.post.accept(self)
            if type(node.cond) != EmptyExpNode:
                node.cond.accept(self)
                cond = self._get_builder().icmp_signed('!=', node.cond.ll_value, int32(0))
            else:
                cond = bool(1)
            self._pop_scope()
            self._get_builder().cbranch(cond, body_block, post_block)

            # after
            self._get_builder().position_at_start(post_block)
            self._push_block(post_block)

    def visitBinaryNode(self, node: BinaryNode):
        node.left.accept(self)
        node.right.accept(self)
        if node.op == '+':
            node.ll_value = self._get_builder().add(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '-':
            node.ll_value = self._get_builder().sub(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '*':
            node.ll_value = self._get_builder().mul(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '/':
            node.ll_value = self._get_builder().sdiv(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '%':
            node.ll_value = self._get_builder().srem(
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '<':
            node.ll_value = self._get_builder().icmp_signed(
                '<',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '>':
            node.ll_value = self._get_builder().icmp_signed(
                '<',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '==':
            node.ll_value = self._get_builder().icmp_signed(
                '==',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '!=':
            node.ll_value = self._get_builder().icmp_signed(
                '!=',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '<=':
            node.ll_value = self._get_builder().icmp_signed(
                '<=',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '>=':
            node.ll_value = self._get_builder().icmp_signed(
                '>=',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '>':
            node.ll_value = self._get_builder().icmp_signed(
                '>',
                node.left.ll_value,
                node.right.ll_value)
        elif node.op == '||':
            explicit_value = self._get_builder().or_(
                node.left.ll_value,
                node.right.ll_value)
            bit_1_value = self._get_builder().icmp_signed(
                '!=',
                explicit_value,
                int32(0))
            node.ll_value = self._get_builder().zext(
                bit_1_value,
                int32)
        elif node.op == '&&':
            explicit_value = self._get_builder().and_(
                node.left.ll_value,
                node.right.ll_value)
            bit_1_value = self._get_builder().icmp_signed(
                '!=',
                explicit_value,
                int32(0))
            node.ll_value = self._get_builder().zext(
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
