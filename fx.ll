; ModuleID = 'samples\fx.c'
source_filename = "samples\\fx.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.28.29337"

@a = dso_local global [10 x [10 x [10 x [10 x float]]]] zeroinitializer, align 16

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca float*, align 8
  store i32 0, i32* %1, align 4
  store float* getelementptr inbounds ([10 x [10 x [10 x [10 x float]]]], [10 x [10 x [10 x [10 x float]]]]* @a, i32 0, i32 0, i32 0, i32 0, i32 0), float** %2, align 8
  %3 = load float*, float** %2, align 8
  %4 = getelementptr inbounds float, float* %3, i64 4000
  %5 = getelementptr inbounds float, float* %4, i64 400
  %6 = getelementptr inbounds float, float* %5, i64 40
  %7 = getelementptr inbounds float, float* %6, i64 4
  store float 0x4014CCCCC0000000, float* %7, align 4
  %8 = load float, float* getelementptr inbounds ([10 x [10 x [10 x [10 x float]]]], [10 x [10 x [10 x [10 x float]]]]* @a, i64 0, i64 4, i64 4, i64 4, i64 4), align 16
  %9 = fptosi float %8 to i32
  ret i32 %9
}

attributes #0 = { noinline nounwind optnone uwtable "disable-tail-calls"="false" "frame-pointer"="none" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 2}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{!"clang version 12.0.0"}
