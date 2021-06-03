; ModuleID = "program"
target triple = "x86_64-pc-linux"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %"a" = alloca i32
  %"b" = alloca i32
  store i32 2, i32* %"b"
  %"c" = alloca i32
  %"d" = alloca i32
  store i32 4, i32* %"d"
  %".5" = load i32, i32* %"d"
  %".6" = add i32 2, %".5"
  store i32 %".6", i32* %"d"
  %".8" = load i32, i32* %"d"
  ret i32 %".8"
}
