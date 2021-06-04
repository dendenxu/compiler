; ModuleID = "program"
target triple = "x86_64-pc-linux"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %"a" = alloca i32
  %".3" = add i32 1, 3
  store i32 %".3", i32* %"a"
  %"b" = alloca i32
  store i32 1, i32* %"b"
  %".6" = load i32, i32* %"a"
  %".7" = icmp eq i32 %".6", 3
  %".8" = icmp ne i1 %".7", 0
  br i1 %".8", label %".2.if", label %".2.else"
.2.if:
  %".10" = mul i32 1, -1
  store i32 %".10", i32* %"a"
  br label %".2.endif"
.2.else:
  %".13" = mul i32 2, -1
  store i32 %".13", i32* %"a"
  br label %".2.endif"
.2.endif:
  %"i" = alloca i32
  store i32 0, i32* %"i"
  %".17" = load i32, i32* %"i"
  %".18" = icmp slt i32 %".17", 10
  %".19" = icmp ne i1 %".18", 0
  br i1 %".19", label %".20", label %".21"
.20:
  %".23" = load i32, i32* %"i"
  store i32 %".23", i32* %"a"
  %".25" = load i32, i32* %"i"
  %".26" = add i32 %".25", 1
  store i32 %".26", i32* %"i"
  %".28" = load i32, i32* %"i"
  %".29" = icmp slt i32 %".28", 10
  %".30" = icmp ne i1 %".29", 0
  br i1 %".30", label %".20", label %".21"
.21:
  %".32" = load i32, i32* %"a"
  ret i32 %".32"
}
