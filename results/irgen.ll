; ModuleID = "program"
target triple = "x86_64-pc-linux"
target datalayout = ""

define i32 @"main"() 
{
.2:
  %".3" = sub i32 1, 1
  %".4" = or i32 %".3", 2
  %".5" = icmp ne i32 %".4", 0
  %".6" = zext i1 %".5" to i32
  ret i32 %".6"
}
