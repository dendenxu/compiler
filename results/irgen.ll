; ModuleID = "program"
target triple = "x86_64-pc-linux"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %"a" = alloca i32
  store i32 1, i32* %"a"
  %"b" = alloca i32
.4:
  %".5" = add i32 1, 2
  store i32 %".5", i32* %"a"
.7:
  ret i32 0
}
