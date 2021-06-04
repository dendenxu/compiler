from llvmlite import ir, binding

make_ptr = ir.PointerType
int32 = ir.IntType(32)
bool = ir.IntType(1)
int1 = ir.IntType(1)