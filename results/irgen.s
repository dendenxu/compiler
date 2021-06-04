	.text
	.file	"irgen.ll"
	.globl	main                    # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %.2
	movl	$4, -4(%rsp)
	movb	$1, %al
	testb	%al, %al
	jne	.LBB0_2
# %bb.1:                                # %.2.if
	movl	$-1, -4(%rsp)
	cmpl	$4, -4(%rsp)
	je	.LBB0_5
	.p2align	4, 0x90
.LBB0_4:                                # %.18
                                        # =>This Inner Loop Header: Depth=1
	movl	-4(%rsp), %eax
	incl	%eax
	movl	%eax, -4(%rsp)
	cmpl	$4, %eax
	jne	.LBB0_4
.LBB0_5:                                # %.19
	movl	-4(%rsp), %eax
	retq
.LBB0_2:                                # %.2.else
	movl	$-2, -4(%rsp)
	cmpl	$4, -4(%rsp)
	jne	.LBB0_4
	jmp	.LBB0_5
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.section	".note.GNU-stack","",@progbits
