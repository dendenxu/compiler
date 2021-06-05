	.text
	.def	 @feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
.set @feat.00, 0
	.file	"irgen.ll"
	.def	 main;
	.scl	2;
	.type	32;
	.endef
	.globl	main                    # -- Begin function main
	.p2align	4, 0x90
main:                                   # @main
.seh_proc main
# %bb.0:                                # %.2
	pushq	%rbp
	.seh_pushreg %rbp
	subq	$416, %rsp              # imm = 0x1A0
	.seh_stackalloc 416
	leaq	128(%rsp), %rbp
	.seh_setframe %rbp, 128
	.seh_endprologue
	movl	$0, -116(%rbp)
.LBB0_1:                                # %.4
                                        # =>This Loop Header: Depth=1
                                        #     Child Loop BB0_5 Depth 2
	movl	-116(%rbp), %eax
	movl	%eax, %ecx
	subl	$10, %ecx
	setl	%dl
	subl	$9, %eax
	jg	.LBB0_4
	jmp	.LBB0_2
.LBB0_2:                                # %.5
                                        #   in Loop: Header=BB0_1 Depth=1
	movl	$16, %eax
	callq	__chkstk
	subq	%rax, %rsp
	movq	%rsp, %rax
	movl	$0, (%rax)
	movq	%rax, -128(%rbp)        # 8-byte Spill
	jmp	.LBB0_5
.LBB0_3:                                # %.6
                                        #   in Loop: Header=BB0_1 Depth=1
	movl	-116(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -116(%rbp)
	jmp	.LBB0_1
.LBB0_4:                                # %.7
	movl	44(%rbp), %eax
	leaq	288(%rbp), %rsp
	popq	%rbp
	retq
.LBB0_5:                                # %.15
                                        #   Parent Loop BB0_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-128(%rbp), %rax        # 8-byte Reload
	movl	(%rax), %ecx
	movl	%ecx, %edx
	subl	$10, %edx
	setl	%r8b
	subl	$9, %ecx
	jg	.LBB0_8
	jmp	.LBB0_6
.LBB0_6:                                # %.16
                                        #   in Loop: Header=BB0_5 Depth=2
	movslq	-116(%rbp), %rax
	imulq	$40, %rax, %rax
	leaq	-112(%rbp), %rcx
	addq	%rax, %rcx
	movq	-128(%rbp), %rax        # 8-byte Reload
	movl	(%rax), %edx
	movl	-116(%rbp), %r8d
	imull	(%rax), %r8d
	movslq	%edx, %r9
	movl	%r8d, (%rcx,%r9,4)
# %bb.7:                                # %.17
                                        #   in Loop: Header=BB0_5 Depth=2
	movq	-128(%rbp), %rax        # 8-byte Reload
	movl	(%rax), %ecx
	addl	$1, %ecx
	movl	%ecx, (%rax)
	jmp	.LBB0_5
.LBB0_8:                                # %.18
                                        #   in Loop: Header=BB0_1 Depth=1
	jmp	.LBB0_3
	.seh_handlerdata
	.text
	.seh_endproc
                                        # -- End function
	.addrsig
