; ModuleID = "program"
target triple = "x86_64-pc-linux"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %"a" = alloca i32
  %".3" = add i32 1, 3
  store i32 %".3", i32* %"a"
  %".5" = load i32, i32* %"a"
  %".6" = icmp eq i32 %".5", 3
  %".7" = icmp ne i1 %".6", 0
  br i1 %".7", label %".2.if", label %".2.else"
.2.if:
  %".9" = mul i32 1, -1
  store i32 %".9", i32* %"a"
  br label %".2.endif"
.2.else:
  %".12" = mul i32 2, -1
  store i32 %".12", i32* %"a"
  br label %".2.endif"
.2.endif:
  %".15" = load i32, i32* %"a"
  ret i32 %".15"
}
