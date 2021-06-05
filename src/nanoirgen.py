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
from nanotraverse import *
import json
import requests
import os


class Visitor:
    pass


class NanoVisitor(Visitor):
    def __init__(self):
        # we do not need list since we only support single filre compiling
        self.cur_module = None
        # we do not need list since we do not support sub-procedure
        self.cur_func_name = ''
        self.builder_stack = []
        self.block_stack = []
        self.scope_stack = []
        self.loop_exit_stack = []
        self.loop_entr_stack = []
        self.defined_funcs = dict()
        self.func_params = dict()
        self.in_global = True

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
        # print('push', self.scope_stack)

    def _pop_scope(self):
        pop = self.scope_stack.pop()
        # print('pop', self.scope_stack)
        return pop

    def _push_block(self, block=None):
        func = self._get_func(self.cur_func_name)
        if block is None:
            block = func.append_basic_block()
        self.block_stack.append(block)

    def _get_block(self):
        return self.block_stack[-1]

    def _pop_block(self):
        return self.block_stack.pop()

    def _add_identifier(self, name, reference):
        if name in self.scope_stack[-1]:
            raise RuntimeError("{name} alredy declared")
        self.scope_stack[-1][name] = reference

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
        self._push_scope()
        self.module = node.module = ir.Module(name='program')
        for func in node.funcs:
            func.accept(self)
        self._pop_scope()

    def visitFuncNode(self, node: FuncNode):
        self.in_global = False
        self._push_scope()

        func_param_type_list = []
        for param in node.params:
            param.accept(self)
            func_param_type_list.append(typ(param))

        node.type.accept(self)
        node.type = ir.FunctionType(typ(node.type), tuple(func_param_type_list))
        node.ref = ir.Function(self.module, typ(node), name=nam(node))
        self.cur_func_name = nam(node.id)
        self._add_func(self.cur_func_name, node.ref)

        self._push_block()
        self._push_builder()

        func_args = list(ref(node).args)
        for i in range(len(func_args)):
            arg_ref = self._get_builder().alloca(func_param_type_list[i])
            self._add_identifier(nam(node.params[i]), arg_ref)
            self._get_builder().store(func_args[i], arg_ref)

        node.block.accept(self)

        if self._get_builder().basic_block.terminator is None:
            self._get_builder().ret(ir.Constant(int32, 0))

        self._pop_builder()
        self._pop_block()
        self._pop_scope()
        self.in_global = True

    def visitCallNode(self, node: CallNode):
        call_func_args = []
        for param in node.params:
            param.accept(self)
            call_func_args.append(val(param))
        func_ref = self._get_func(nam(node))
        node.value = self._get_builder().call(func_ref, tuple(call_func_args))

    def visitParamNode(self, node: ParamNode):
        node.type.accept(self)

    def visitArrSubNode(self, node: ArrSubNode):
        node.subee.accept(self)
        node.suber.accept(self)
        node.ref = self._get_builder().gep(ref(node.subee),
                                           [ir.Constant(int32, 0),
                                            val(node.suber), ])
        node.value = self._get_builder().load(node.ref)

    def visitTypeNode(self, node: TypeNode):
        if node._is_ptr:
            node.typestr.accept(self)
            node.type = make_ptr(typ(node.typestr))
        elif node.typestr == 'int':
            node.type = ir.IntType(32)

    def visitBlockNode(self, node: BlockNode):
        self._push_scope()
        for stmt in node.stmts:
            stmt.accept(self)
        return self._pop_scope()

    def visitRetNode(self, node: RetNode):
        node.exp.accept(self)
        self._get_builder().ret(val(node.exp))

    def visitIDNode(self, node: IDNode):
        item = self._get_identifier(node.name)
        if item is None:
            raise RuntimeError(node.name, "not declared")
        node.ref = item
        node.value = self._get_builder().load(node.ref)

    def visitIntNode(self, node: IntNode):
        node.value = ir.Constant(int32, node.value)

    # def visitPrimNode(self, node: BinaryNode):
    #     node.node.accept(self)
    #     node.value = val(node.node)

    def visitUnaryNode(self, node: UnaryNode):
        node.node.accept(self)
        if node.op == '+':
            node.value = node.node.value
        elif node.op == '-':
            node.value = self._get_builder().mul(val(node.node),
                                                 ir.Constant(int32, -1))
        elif node.op == '!':
            node.value = self._get_builder().icmp_signed('==',
                                                         val(node.node),
                                                         ir.Constant(int32, 0))
        elif node.op == '~':
            node.value = self._get_builder().not_(val(node.node))
        elif node.op == '*':
            node.ref = self._get_builder().load(ref(node.node))
            node.value = self._get_builder().load(node.ref)
        elif node.op == '&':
            node.value = ref(node.node)

    def visitDecNode(self, node: DecNode):
        node.type.accept(self)
        node.type = typ(node.type)
        if len(node.arr):
            for a in reversed(node.arr):
                node.type = ir.ArrayType(node.type, a)
        if self.in_global:
            node.item = ir.GlobalVariable(self.module, node.type, nam(node.id))
            if node.init is not None:
                node.init.accept(self)
                node.item.initializer = val(node.init)
        else:
            node.item = self._get_builder().alloca(node.type)
            if node.init is not None:
                node.init.accept(self)
                self._get_builder().store(val(node.init), node.item)
        self._add_identifier(nam(node.id), node.item)

    def visitAssNode(self, node: AssNode):
        node.unary.accept(self)
        node.exp.accept(self)
        self._get_builder().store(val(node.exp), ref(node.unary))

    def visitContinueNode(self, node: ContinueNode):
        self._get_builder().branch(self.loop_entr_stack[-1])

    def visitBreakNode(self, node: BreakNode):
        print(self.loop_exit_stack)
        self._get_builder().branch(self.loop_exit_stack[-1])

    def visitIfStmtNode(self, node: IfStmtNode):
        node.cond.accept(self)
        pred = self._get_builder().icmp_signed('!=',
                                               val(node.cond),
                                               ir.Constant(int32, 0))
        if type(node.ifbody) == EmptyStmtNode:
            return
        if type(node.elsebody) == EmptyStmtNode:
            # then_block = self._get_builder().append_basic_block()
            # post_block = self._get_builder().append_basic_block()
            # self._get_builder().cbranch(pred, then_block, post_block)
            # self._get_builder().position_at_start(then_block)
            # self._push_scope()
            # node.ifbody.accept(self)
            # self._pop_scope()
            # self._get_builder().branch(post_block)
            # self._get_builder().position_at_start(post_block)
            with self._get_builder().if_then(pred) as then:
                # self._push_block(then)
                self._push_scope()
                node.ifbody.accept(self)
                self._pop_scope()
                # self._pop_block()
        else:
            # then_block = self._get_builder().append_basic_block()
            # otherwise_block = self._get_builder().append_basic_block()
            # post_block = self._get_builder().append_basic_block()
            # self._get_builder().cbranch(pred, then_block, otherwise_block)
            # self._get_builder().position_at_start(then_block)
            # self._push_scope()
            # node.ifbody.accept(self)
            # self._get_builder().branch(post_block)
            # self._pop_scope()
            # self._get_builder().position_at_start(otherwise_block)
            # self._push_scope()
            # node.elsebody.accept(self)
            # self._get_builder().branch(post_block)
            # self._pop_scope()
            # self._get_builder().position_at_start(post_block)
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

        # print('pre', node.pre)
        # print('cond', node.cond)
        # print('body', node.body)
        # print('post', node.post)

        # do-while
        if node.cond == 'while':
            """ do-while
                ...
                branch body_block
            body_block:
                body...
                branch cond_block
            cond_block [continue target]:
                cond...
                branch(cond, body_block, tail_block)
            tail_block [break target]:
                ...
            """
            node.cond = node.body
            node.body = node.pre
            node.pre = node.post

            # scope_new_0
            self._push_scope()
            body_block = self._get_builder().append_basic_block()
            cond_block = self._get_builder().append_basic_block()
            tail_block = self._get_builder().append_basic_block()
            self.loop_entr_stack.append(cond_block)
            self.loop_exit_stack.append(tail_block)
            self._get_builder().branch(body_block)
            self._get_builder().position_at_start(body_block)

            # scope_new_1 auto created when visitBlockNode
            node.body.accept(self)
            self._get_builder().branch(cond_block)
            self._get_builder().position_at_start(cond_block)

            node.cond.accept(self)
            cond = self._get_builder().icmp_signed('!=',
                                                   val(node.cond),
                                                   ir.Constant(int32, 0))
            self._get_builder().cbranch(cond, body_block, tail_block)
            # exit
            self._get_builder().position_at_start(tail_block)
            self._pop_scope()

            self.loop_entr_stack.pop()
            self.loop_exit_stack.pop()

        # while & for
        else:
            """ for & while
                ...
                pre...
                branch cond_block
            cond_block:
                cond...
                branch(cond, body_block, tail_block)
            body_block:
                body...
                branch post_block
            post_block [continue target]:
                post...
                branch cond_block
            tail_block [break target]:
                ...
            """

            cond_block = self._get_builder().append_basic_block()
            body_block = self._get_builder().append_basic_block()
            post_block = self._get_builder().append_basic_block()
            tail_block = self._get_builder().append_basic_block()
            self.loop_entr_stack.append(post_block)
            self.loop_exit_stack.append(tail_block)

            print(tail_block)

            # scope_new_0
            self._push_scope()
            if type(node.pre) != EmptyStmtNode:
                node.pre.accept(self)
            self._get_builder().branch(cond_block)

            # entrance
            self._get_builder().position_at_start(cond_block)
            if type(node.cond) != EmptyExpNode:
                node.cond.accept(self)
                cond = self._get_builder().icmp_signed('!=',
                                                       val(node.cond),
                                                       ir.Constant(int32, 0))
            else:
                cond = bool(1)
            self._get_builder().cbranch(cond, body_block, tail_block)

            # scope_new_1 auto created when visitBlockNode
            self._get_builder().position_at_start(body_block)
            node.body.accept(self)
            self._get_builder().branch(post_block)

            # return to scope 0
            self._get_builder().position_at_start(post_block)
            if type(node.post) != EmptyStmtNode:
                node.post.accept(self)
            self._get_builder().branch(cond_block)
            self._pop_scope()

            # after
            self._get_builder().position_at_start(tail_block)

            self.loop_entr_stack.pop()
            self.loop_exit_stack.pop()

    def visitBinaryNode(self, node: BinaryNode):
        node.left.accept(self)
        node.right.accept(self)
        if node.op == '+':
            node.value = self._get_builder().add(
                val(node.left),
                val(node.right))
        elif node.op == '-':
            node.value = self._get_builder().sub(
                val(node.left),
                val(node.right))
        elif node.op == '*':
            node.value = self._get_builder().mul(
                val(node.left),
                val(node.right))
        elif node.op == '/':
            node.value = self._get_builder().sdiv(
                val(node.left),
                val(node.right))
        elif node.op == '%':
            node.value = self._get_builder().srem(
                val(node.left),
                val(node.right))
        elif node.op == '<':
            node.value = self._get_builder().icmp_signed(
                '<',
                val(node.left),
                val(node.right))
        elif node.op == '>':
            node.value = self._get_builder().icmp_signed(
                '>',
                val(node.left),
                val(node.right))
        elif node.op == '==':
            node.value = self._get_builder().icmp_signed(
                '==',
                val(node.left),
                val(node.right))
        elif node.op == '!=':
            node.value = self._get_builder().icmp_signed(
                '!=',
                val(node.left),
                val(node.right))
        elif node.op == '<=':
            node.value = self._get_builder().icmp_signed(
                '<=',
                val(node.left),
                val(node.right))
        elif node.op == '>=':
            node.value = self._get_builder().icmp_signed(
                '>=',
                val(node.left),
                val(node.right))
        elif node.op == '>':
            node.value = self._get_builder().icmp_signed(
                '>',
                val(node.left),
                val(node.right))
        elif node.op == '||':
            explicit_value = self._get_builder().or_(
                val(node.left),
                val(node.right))
            bit_1_value = self._get_builder().icmp_signed(
                '!=',
                explicit_value,
                int32(0))
            node.value = self._get_builder().zext(
                bit_1_value,
                int32)
        elif node.op == '&&':
            explicit_value = self._get_builder().and_(
                val(node.left),
                val(node.right))
            bit_1_value = self._get_builder().icmp_signed(
                '!=',
                explicit_value,
                int32(0))
            node.value = self._get_builder().zext(
                bit_1_value,
                int32)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-input", default="samples/fx.c", type=str)
    parser.add_argument("-output", default="results/irgen.ll", type=str)
    parser.add_argument("-target", default="x86_64-pc-linux", type=str)
    parser.add_argument("-url", default="http://neon-cubes.xyz:8000/src/tree.json", type=str)
    parser.add_argument("-generate", action="store_true", default=True, dest='generate', help="Whether to generate the target machine code")
    parser.add_argument("-ext", default="", type=str, help="Executable file extension")
    args = parser.parse_args()
    with open(args.input, 'r', encoding='utf-8') as f:
        content = f.read()
        lexer = NanoLexer()
        lexer.build()
        parser = NanoParser()
        parser.build()
        root = parser.parse(content, lexer=lexer)
        print(colored(f"Abstract Syntax Tree:", "yellow", attrs=["bold"]))
        print(root)

        tree = traverse(root)
        addsize(tree)
        payload = json.dumps(tree)
        r = requests.post(url=args.url, data=payload)
        print(colored(f"POST response: {r}", "yellow", attrs=["bold"]))

        visitor = NanoVisitor()
        visitor.visitProgNode(root)
        ir = str(root.module).replace('unknown-unknown-unknown',
                                      args.target)
        print(colored(f"LLVM IR:", "yellow", attrs=["bold"]))
        print(f"{ir}")
    with open(args.output, 'w') as I:
        I.write(ir)

    if args.generate:
        path, basename = os.path.split(args.output)
        basenamenoext = os.path.splitext(basename)[0]
        ass = os.path.join(path, basenamenoext + '.s')
        exe = os.path.join(path, basenamenoext + args.ext)

        os.system(' '.join(["clang", args.output, "-S", "-o", ass]))
        os.system(' '.join(["clang", ass, "-o", exe]))
        print(colored(f"IR/Assembly/Executable stored at: {path}", "yellow", attrs=["bold"]))
