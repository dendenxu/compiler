; ModuleID = 'samples\matmul.c'
source_filename = "samples\\matmul.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.28.29337"

@a = dso_local global [2 x [2 x i32]] zeroinitializer, align 16
@b = dso_local global [2 x [2 x i32]] zeroinitializer, align 16
@c = dso_local global [2 x [2 x i32]] zeroinitializer, align 16

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @mulMatrix(i32 %0, i32* %1, i32* %2, i32* %3) #0 {
  %5 = alloca i32, align 4
  %6 = alloca i32*, align 8
  %7 = alloca i32*, align 8
  %8 = alloca i32*, align 8
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  %11 = alloca i32, align 4
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  store i32* %3, i32** %6, align 8
  store i32* %2, i32** %7, align 8
  store i32* %1, i32** %8, align 8
  store i32 %0, i32* %9, align 4
  store i32 0, i32* %10, align 4
  br label %14

14:                                               ; preds = %85, %4
  %15 = load i32, i32* %10, align 4
  %16 = load i32, i32* %9, align 4
  %17 = icmp slt i32 %15, %16
  br i1 %17, label %18, label %88

18:                                               ; preds = %14
  store i32 0, i32* %11, align 4
  br label %19

19:                                               ; preds = %82, %18
  %20 = load i32, i32* %11, align 4
  %21 = load i32, i32* %9, align 4
  %22 = icmp slt i32 %20, %21
  br i1 %22, label %23, label %85

23:                                               ; preds = %19
  %24 = load i32*, i32** %6, align 8
  %25 = load i32, i32* %10, align 4
  %26 = load i32, i32* %9, align 4
  %27 = mul nsw i32 %25, %26
  %28 = sext i32 %27 to i64
  %29 = getelementptr inbounds i32, i32* %24, i64 %28
  %30 = load i32, i32* %11, align 4
  %31 = sext i32 %30 to i64
  %32 = getelementptr inbounds i32, i32* %29, i64 %31
  store i32 0, i32* %32, align 4
  store i32 0, i32* %12, align 4
  br label %33

33:                                               ; preds = %37, %23
  %34 = load i32, i32* %12, align 4
  %35 = load i32, i32* %9, align 4
  %36 = icmp slt i32 %34, %35
  br i1 %36, label %37, label %82

37:                                               ; preds = %33
  %38 = load i32*, i32** %6, align 8
  %39 = load i32, i32* %10, align 4
  %40 = load i32, i32* %9, align 4
  %41 = mul nsw i32 %39, %40
  %42 = sext i32 %41 to i64
  %43 = getelementptr inbounds i32, i32* %38, i64 %42
  %44 = load i32, i32* %11, align 4
  %45 = sext i32 %44 to i64
  %46 = getelementptr inbounds i32, i32* %43, i64 %45
  %47 = load i32, i32* %46, align 4
  store i32 %47, i32* %13, align 4
  %48 = load i32, i32* %13, align 4
  %49 = load i32*, i32** %8, align 8
  %50 = load i32, i32* %10, align 4
  %51 = load i32, i32* %9, align 4
  %52 = mul nsw i32 %50, %51
  %53 = sext i32 %52 to i64
  %54 = getelementptr inbounds i32, i32* %49, i64 %53
  %55 = load i32, i32* %12, align 4
  %56 = sext i32 %55 to i64
  %57 = getelementptr inbounds i32, i32* %54, i64 %56
  %58 = load i32, i32* %57, align 4
  %59 = load i32*, i32** %7, align 8
  %60 = load i32, i32* %12, align 4
  %61 = load i32, i32* %9, align 4
  %62 = mul nsw i32 %60, %61
  %63 = sext i32 %62 to i64
  %64 = getelementptr inbounds i32, i32* %59, i64 %63
  %65 = load i32, i32* %11, align 4
  %66 = sext i32 %65 to i64
  %67 = getelementptr inbounds i32, i32* %64, i64 %66
  %68 = load i32, i32* %67, align 4
  %69 = mul nsw i32 %58, %68
  %70 = add nsw i32 %48, %69
  %71 = load i32*, i32** %6, align 8
  %72 = load i32, i32* %10, align 4
  %73 = load i32, i32* %9, align 4
  %74 = mul nsw i32 %72, %73
  %75 = sext i32 %74 to i64
  %76 = getelementptr inbounds i32, i32* %71, i64 %75
  %77 = load i32, i32* %11, align 4
  %78 = sext i32 %77 to i64
  %79 = getelementptr inbounds i32, i32* %76, i64 %78
  store i32 %70, i32* %79, align 4
  %80 = load i32, i32* %12, align 4
  %81 = add nsw i32 %80, 1
  store i32 %81, i32* %12, align 4
  br label %33, !llvm.loop !3

82:                                               ; preds = %33
  %83 = load i32, i32* %11, align 4
  %84 = add nsw i32 %83, 1
  store i32 %84, i32* %11, align 4
  br label %19, !llvm.loop !5

85:                                               ; preds = %19
  %86 = load i32, i32* %10, align 4
  %87 = add nsw i32 %86, 1
  store i32 %87, i32* %10, align 4
  br label %14, !llvm.loop !6

88:                                               ; preds = %14
  %89 = load i32, i32* %5, align 4
  ret i32 %89
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @initMatrix(i32 %0, i32* %1) #0 {
  %3 = alloca i32, align 4
  %4 = alloca i32*, align 8
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  store i32* %1, i32** %4, align 8
  store i32 %0, i32* %5, align 4
  store i32 0, i32* %8, align 4
  store i32 0, i32* %6, align 4
  br label %9

9:                                                ; preds = %31, %2
  %10 = load i32, i32* %6, align 4
  %11 = icmp slt i32 %10, 2
  br i1 %11, label %12, label %34

12:                                               ; preds = %9
  store i32 0, i32* %7, align 4
  br label %13

13:                                               ; preds = %16, %12
  %14 = load i32, i32* %7, align 4
  %15 = icmp slt i32 %14, 2
  br i1 %15, label %16, label %31

16:                                               ; preds = %13
  %17 = load i32, i32* %8, align 4
  %18 = add nsw i32 %17, 1
  store i32 %18, i32* %8, align 4
  %19 = load i32, i32* %8, align 4
  %20 = load i32*, i32** %4, align 8
  %21 = load i32, i32* %6, align 4
  %22 = load i32, i32* %5, align 4
  %23 = mul nsw i32 %21, %22
  %24 = sext i32 %23 to i64
  %25 = getelementptr inbounds i32, i32* %20, i64 %24
  %26 = load i32, i32* %7, align 4
  %27 = sext i32 %26 to i64
  %28 = getelementptr inbounds i32, i32* %25, i64 %27
  store i32 %19, i32* %28, align 4
  %29 = load i32, i32* %7, align 4
  %30 = add nsw i32 %29, 1
  store i32 %30, i32* %7, align 4
  br label %13, !llvm.loop !7

31:                                               ; preds = %13
  %32 = load i32, i32* %6, align 4
  %33 = add nsw i32 %32, 1
  store i32 %33, i32* %6, align 4
  br label %9, !llvm.loop !8

34:                                               ; preds = %9
  %35 = load i32, i32* %3, align 4
  ret i32 %35
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  store i32 0, i32* %1, align 4
  %2 = call i32 @initMatrix(i32 2, i32* getelementptr inbounds ([2 x [2 x i32]], [2 x [2 x i32]]* @a, i32 0, i32 0, i32 0))
  %3 = call i32 @mulMatrix(i32 2, i32* getelementptr inbounds ([2 x [2 x i32]], [2 x [2 x i32]]* @a, i32 0, i32 0, i32 0), i32* getelementptr inbounds ([2 x [2 x i32]], [2 x [2 x i32]]* @a, i32 0, i32 0, i32 0), i32* getelementptr inbounds ([2 x [2 x i32]], [2 x [2 x i32]]* @b, i32 0, i32 0, i32 0))
  %4 = call i32 @mulMatrix(i32 2, i32* getelementptr inbounds ([2 x [2 x i32]], [2 x [2 x i32]]* @b, i32 0, i32 0, i32 0), i32* getelementptr inbounds ([2 x [2 x i32]], [2 x [2 x i32]]* @b, i32 0, i32 0, i32 0), i32* getelementptr inbounds ([2 x [2 x i32]], [2 x [2 x i32]]* @c, i32 0, i32 0, i32 0))
  %5 = load i32, i32* getelementptr inbounds ([2 x [2 x i32]], [2 x [2 x i32]]* @b, i64 0, i64 0, i64 0), align 16
  ret i32 %5
}

attributes #0 = { noinline nounwind optnone uwtable "disable-tail-calls"="false" "frame-pointer"="none" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 2}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{!"clang version 12.0.0"}
!3 = distinct !{!3, !4}
!4 = !{!"llvm.loop.mustprogress"}
!5 = distinct !{!5, !4}
!6 = distinct !{!6, !4}
!7 = distinct !{!7, !4}
!8 = distinct !{!8, !4}
