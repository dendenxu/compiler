; ModuleID = "program"
target triple = "x86_64-pc-linux"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %"a" = alloca i32
  %".3" = add i32 1, 2
  store i32 %".3", i32* %"a"
  %".5" = load i32, i32* %"a"
  %".6" = icmp eq i32 %".5", 3
  %".7" = icmp ne i1 %".6", 0
  %".8" = load i32, i32* %"a"
  ret i32 %".8"
}
