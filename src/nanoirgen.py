from llvmlite.ir import builder
from llvmlite.ir.instructions import ICMPInstr
from ply import yacc
from nanoast import *
from nanolex import NanoLexer
from nanoyacc import NanoParser
from nanotype import *
from nanoerror import *
import nanotype as ntp
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
        self.is_func_body = False
        self.n_errors = 0
        self.n_warnings = 0
    
    def _exit(self):
        print(f"{self.n_errors}"+colored(" error(s)", "red")+f", {self.n_warnings}"+colored(" warning(s)", "yellow"))
        exit(-1)

    def _push_builder(self, builder=None):
        if builder is not None:
            self.builder_stack.append(builder)
        else:
            block = self._get_block()
            builder = ir.IRBuilder(block)
            self.builder_stack.append(builder)

    def _get_builder(self) -> ir.IRBuilder:
        if self.builder_stack == []:
            return None
        return self.builder_stack[-1]

    def _pop_builder(self):
        pop = self.builder_stack.pop()
        return pop

    def _push_scope(self):
        self.scope_stack.append(dict())

    def _pop_scope(self):
        pop = self.scope_stack.pop()
        return pop

    def _push_block(self, block=None):
        func = self._get_func(self.cur_func_name)
        if block is None:
            block = func.append_basic_block()
        self.block_stack.append(block)

    def _get_block(self):
        if self.block_stack == []:
            return None
        return self.block_stack[-1]

    def _pop_block(self):
        if self.block_stack == []:
            return None
        return self.block_stack.pop()

    def _add_identifier(self, name, reference, type):
        if self.scope_stack == []:
            return None
        if name in self.scope_stack[-1]:
            return None
        self.scope_stack[-1][name] = {'ref':reference, 'typ':type}
        return self.scope_stack[-1][name]

    def _get_identifier(self, name):
        for d in self.scope_stack[::-1]:  # reversing the scope_block
            if name in d:
                return d[name]['ref']
        return None
    
    def _get_id_type(self, name):
        for d in self.scope_stack[::-1]:  # reversing the scope_block
            if name in d:
                return d[name]['typ']
        return None

    def _add_func(self, name, func, params=dict()):
        if name in self.defined_funcs.keys():
            return None
        self.defined_funcs[name] = [func, params]
        return self.defined_funcs[name]

    def _get_func(self, name):
        if name in self.defined_funcs.keys():
            return self.defined_funcs[name][0]
        return None

    def visitProgNode(self, node: ProgNode):
        self._push_scope()
        self.module = node.module = ir.Module(name='program')
        for func in node.funcs:
            func.accept(self)
        self._pop_scope()
        print(f"{self.n_errors}"+colored(" error(s)", "red")+f", {self.n_warnings}"+colored(" warning(s)", "yellow"))
        if self.n_errors:
            self._exit()

    def visitFuncNode(self, node: FuncNode):
        self.in_global = False
        self._push_scope()

        func_param_type_list = []
        for param in node.params:
            param.accept(self)
            param_typ = typ(param)
            if param_typ == void:
                continue
            func_param_type_list.append(typ(param))

        node.type.accept(self)
        node.type = ir.FunctionType(typ(node.type), tuple(func_param_type_list))
        if self._get_func(nam(node)) is not None:
            self.n_errors += 1
            print(IRedecFatal(nam(node)))
            self._exit()
            
        node.ref = ir.Function(self.module, typ(node), name=nam(node))
        self._add_func(nam(node), node.ref)
        self.cur_func_name = nam(node.id)
        
        self._push_block()
        self._push_builder()

        func_args = list(ref(node).args)
        for i in range(len(func_args)):
            arg_ref = self._get_builder().alloca(func_param_type_list[i])
            res = self._add_identifier(nam(node.params[i]), arg_ref, func_param_type_list[i])
            if res is None:
                self.n_errors += 1
                print(IRedecError(nam(node.params[i])))
            self._get_builder().store(func_args[i], arg_ref)

        node.block.accept(self)

        if self._get_builder().basic_block.terminator is None:
            ret_type = self._get_func(self.cur_func_name).ftype.return_type
            if ret_type == void:
                self._get_builder().ret_void()
            else:
                self._get_builder().ret(ir.Constant(ret_type, 0))
            self.n_warnings += 1
            print(IFuncExitWarning(nam(node)))

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
        if func_ref is None:
            self.n_errors += 1
            print(IUndecFatal(nam(node)))
            self._exit()
        func_args = list(func_ref.ftype.args)
        if len(func_ref.ftype.args) != len(call_func_args):
            self.n_errors += 1
            print(IArgsLenUnmatchFatal(len(call_func_args),len(func_ref.ftype.args)))
            self._exit()
        else:
            for i in range(len(call_func_args)):
                if exp_type(node.params[i]) != str(func_args[i]):
                    self.n_errors += 1
                    print(IArgsUnmatchFatal(exp_type(node.params[i]),str(func_args[i])))
                    self._exit()
        node.value = self._get_builder().call(func_ref, tuple(call_func_args))
        node.exp_type = str(func_ref.ftype.return_type)

    def visitParamNode(self, node: ParamNode):
        node.type.accept(self)
        node.exp_type = exp_type(node.type)

    def visitArrSubNode(self, node: ArrSubNode):
        node.subee.accept(self)
        node.suber.accept(self)
        if type(ref(node.subee).type.pointee) != ir.ArrayType:
            self.n_errors += 1
            print(TMismatchError(str(ref(node.subee).type.pointee), 'arrayType'))
            self._exit()
        node.ref = self._get_builder().gep(ref(node.subee),
                                           [ir.Constant(int32, 0),
                                            val(node.suber), ])
        node.exp_type = str(node.ref.type.pointee)

    def visitTypeNode(self, node: TypeNode):
        if node._is_ptr:
            node.typestr.accept(self)
            node.type = make_ptr(typ(node.typestr))
        elif node.typestr == 'int':
            node.type = int32
        elif node.typestr == 'void':
            node.type = void
        elif node.typestr == 'float':
            node.type = flpt
        else:
            raise NotImplementedError

    def visitBlockNode(self, node: BlockNode, scope=None):
        if scope is None:
            self._push_scope()
        else:
            self._push_scope(scope)
        for stmt in node.stmts:
            stmt.accept(self)
        return self._pop_scope()

    def visitRetNode(self, node: RetNode):
        node.exp.accept(self)
        cur_func_ret_type = str(self._get_func(self.cur_func_name).ftype.return_type)
        if exp_type(node.exp) != cur_func_ret_type:
            self.n_errors += 1
            print(TMismatchError(exp_type(node.exp), cur_func_ret_type))
            self._exit()
        if exp_type(node.exp) != 'void':
            self._get_builder().ret(val(node.exp))
        else:
            self._get_builder().ret_void()

    def visitIDNode(self, node: IDNode):
        item = self._get_identifier(node.name)
        if item is None:
            self.n_errors += 1
            print(IUndecFatal(nam(node)))
            self._exit()
        node.ref = item
        node.type = item.type

    def visitIntNode(self, node: IntNode):
        node.value = ir.Constant(int32, node.value)
        node.type = int32
    
    def visitFloatNode(self, node: FloatNode):
        node.value = ir.Constant(flpt, node.value)
        node.type = flpt

    # def visitPrimNode(self, node: BinaryNode):
    #     node.node.accept(self)
    #     node.value = val(node.node)

    def visitUnaryNode(self, node: UnaryNode):
        node.node.accept(self)
        if node.op == '+':
            node.value = node.node.value
        elif node.op == '-':
            node.value = self._get_builder().neg(val(node.node))
        elif node.op == '!':
            node.value = self._get_builder().icmp_signed('==',
                                                         val(node.node),
                                                         ir.Constant(int32, 0))
        elif node.op == '~':
            node.value = self._get_builder().not_(val(node.node))
        elif node.op == '*':
            node.ref = val(node.node)
        elif node.op == '&':
            node.value = ref(node.node)
        elif type(node.op) == TypeNode:
            # type casting
            node.op.accept(self)
            try:
                node.value = cast(val(node.node), exp_type(node.op), ref(node.node))
            except Exception as e:
                node.value = cast(val(node.node), exp_type(node.op))
        else:
            raise NotImplementedError
        node.exp_type = str(val(node).type)

    def visitDecNode(self, node: DecNode):
        node.type.accept(self)
        node.type = typ(node.type)
        if len(node.arr):
            for a in list(reversed(node.arr)):
                node.type = ir.ArrayType(node.type, a)
        if self.in_global:
            try:
                node.item = ir.GlobalVariable(self.module, node.type, nam(node.id))
            except Exception as e:
                self.n_errors += 1
                print(IRedecError(nam(node.id)))
                self._exit()
            node.item.linkage = 'internal'
            if node.init is not None:
                node.init.accept(self)
                node.item.initializer = val(node.init)
            else:
                self.n_warnings += 1
                print(IGlobalNotInitWarning(nam(node.id)))
        else:
            node.item = self._get_builder().alloca(node.type)
            if node.init is not None:
                node.init.accept(self)
                self._get_builder().store(val(node.init), node.item)
        res = self._add_identifier(nam(node.id), node.item, node.type)
        if res is None:
            self.n_errors += 1
            print(IRedecError(nam(node.id)))
            self._exit()

    def visitAssNode(self, node: AssNode):
        node.unary.accept(self)
        node.exp.accept(self)
        if exp_type(node.exp) != exp_type(node.unary):
            self.n_errors += 1
            print(TMismatchError(exp_type(node.exp), exp_type(node.unary)))
            self._exit()
        node.value = val(node.exp)
        self._get_builder().store(node.value, ref(node.unary))

    def visitContinueNode(self, node: ContinueNode):
        self._get_builder().branch(self.loop_entr_stack[-1])

    def visitBreakNode(self, node: BreakNode):
        self._get_builder().branch(self.loop_exit_stack[-1])

    def visitIfStmtNode(self, node: IfStmtNode):
        node.cond.accept(self)
        pred = self._get_builder().icmp_signed('!=',
                                               val(node.cond),
                                               ir.Constant(int32, 0))
        if type(node.ifbody) == EmptyStmtNode:
            return
        if type(node.elsebody) == EmptyStmtNode:
            with self._get_builder().if_then(pred) as then:
                self._push_scope()
                node.ifbody.accept(self)
                self._pop_scope()
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
                cond = int1(1)
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
        node.exp_type = binCompat(node.left, node.right, node.op)
        if exp_type(node.left) == 'float' or exp_type(node.right) == 'float':
            if node.op == '+':
                node.value = self._get_builder().fadd(
                    val(node.left),
                    val(node.right))
            elif node.op == '-':
                node.value = self._get_builder().fsub(
                    val(node.left),
                    val(node.right))
            elif node.op == '*':
                node.value = self._get_builder().fmul(
                    val(node.left),
                    val(node.right))
            elif node.op == '/':
                node.value = self._get_builder().fdiv(
                    val(node.left),
                    val(node.right))
            elif node.op == '%':
                node.value = self._get_builder().frem(
                    val(node.left),
                    val(node.right))
            elif node.op == '<':
                node.value = self._get_builder().fcmp_ordered(
                    '<',
                    val(node.left),
                    val(node.right))
            elif node.op == '>':
                node.value = self._get_builder().fcmp_ordered(
                    '>',
                    val(node.left),
                    val(node.right))
            elif node.op == '==':
                node.value = self._get_builder().fcmp_ordered(
                    '==',
                    val(node.left),
                    val(node.right))
            elif node.op == '!=':
                node.value = self._get_builder().fcmp_ordered(
                    '!=',
                    val(node.left),
                    val(node.right))
            elif node.op == '<=':
                node.value = self._get_builder().fcmp_ordered(
                    '<=',
                    val(node.left),
                    val(node.right))
            elif node.op == '>=':
                node.value = self._get_builder().fcmp_ordered(
                    '>=',
                    val(node.left),
                    val(node.right))
            elif node.op == '>':
                node.value = self._get_builder().fcmp_ordered(
                    '>',
                    val(node.left),
                    val(node.right))
            elif node.op == '||':
                node.value = self._get_builder().or_(
                    val(node.left),
                    val(node.right))
            elif node.op == '&&':
                node.value = self._get_builder().and_(
                    val(node.left),
                    val(node.right))
            else:
                raise NotImplementedError
        elif exp_type(node.left) in ('i32','i1') and exp_type(node.right) in ('i32','i1'):
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
                node.value = self._get_builder().or_(
                    val(node.left),
                    val(node.right))
            elif node.op == '&&':
                node.value = self._get_builder().and_(
                    val(node.left),
                    val(node.right))
            else:
                raise NotImplementedError
        elif exp_type(node.left) == 'i32*' and exp_type(node.right) == 'i32':
            node.value = self._get_builder().gep(
                val(node.left), [val(node.right)])
        elif exp_type(node.left) == 'float*' and exp_type(node.right) == 'i32':
            node.value = self._get_builder().gep(
                val(node.left), [val(node.right)])
        else:
            self.n_errors += 1
            print(TMismatchError(exp_type(node.left), exp_type(node.right)))
            self._exit()
            raise NotImplementedError

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-input", default="samples/fx.c", type=str)
    parser.add_argument("-output", default="results/irgen.ll", type=str)
    parser.add_argument("-target", default="x86_64-pc-linux", type=str)
    parser.add_argument("-url", default="http://neon-cubes.xyz:8000/src/tree.json", type=str)
    parser.add_argument("-tree", type=str)
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

        # tree = traverse(root)
        # addinfo(tree, args.input)
        # payload = json.dumps(tree)
        # if args.tree:
        #     with open(args.tree, 'w') as f:
        #         f.write(payload)
        #     print(colored(f"Saved Structrued Tree to {args.tree}", 'yellow', attrs=['bold']))

        # r = requests.post(url=args.url, data=payload)
        # print(colored(f"POST response: {r}", "yellow", attrs=["bold"]))

        # global tp_visitor
        visitor = ntp.tp_visitor = NanoVisitor()
        
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
