; ModuleID = "program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %".3" = add i32 1, 2
  %".4" = sub i32 %".3", 3
  ret i32 %".4"
}
