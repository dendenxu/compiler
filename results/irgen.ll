; ModuleID = "program"
target triple = "x86_64-pc-linux"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %"a" = alloca i32
  %".3" = add i32 1, 1
  store i32 %".3", i32* %"a"
  %"b" = alloca i32
  store i32 2, i32* %"b"
.6:
  %".7" = add i32 2, 1
  store i32 %".7", i32* %"a"
.9:
  ret i32 0
}
