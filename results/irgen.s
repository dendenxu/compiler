	.text
	.file	"irgen.ll"
	.globl	main                    # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %.2
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$16, %rsp
	movl	$4, -4(%rbp)
	movl	$1, -8(%rbp)
	movb	$1, %al
	testb	%al, %al
	jne	.LBB0_2
# %bb.1:                                # %.2.if
	movl	$-1, -4(%rbp)
	jmp	.LBB0_3
.LBB0_2:                                # %.2.else
	movl	$-2, -4(%rbp)
.LBB0_3:                                # %.2.endif
	movq	%rsp, %rcx
	leaq	-16(%rcx), %rax
	movq	%rax, %rsp
	movl	$0, -16(%rcx)
	xorl	%ecx, %ecx
	testb	%cl, %cl
	jne	.LBB0_5
	.p2align	4, 0x90
.LBB0_4:                                # %.20
                                        # =>This Inner Loop Header: Depth=1
	movl	(%rax), %ecx
	movl	%ecx, -4(%rbp)
	movl	(%rax), %ecx
	incl	%ecx
	movl	%ecx, (%rax)
	cmpl	$10, %ecx
	jl	.LBB0_4
.LBB0_5:                                # %.21
	movl	-4(%rbp), %eax
	movq	%rbp, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.section	".note.GNU-stack","",@progbits
