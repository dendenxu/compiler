; ModuleID = "program"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %".3" = and i32 3, 2
  %".4" = icmp ne i32 %".3", 0
  ret i1 %".4"
}
