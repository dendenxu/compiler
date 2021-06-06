from llvmlite import ir, binding
from termcolor import colored

class EError():
    pass

class EWarning():
    pass

class EFatal():
    pass

class IArgsLenUnmatchFatal(EFatal):
    def __init__(self, len1, len2):
        self.len1 = len1
        self.len2 = len2
    def __str__(self):
        return colored("IArgsLenUnmatchFatal: ", "red") + \
            "the length of the calling args is " + \
            colored(f"{self.len1}", "magenta") + \
            " is not matched with the length of the target function args which is " + \
            colored(f"{self.len2}", "magenta")


class IArgsUnmatchFatal(EFatal):
    def __init__(self, src_type: str, tgt_type: str):
        self.src_type = src_type
        self.tgt_type = tgt_type
    def __str__(self):
        return colored("IArgsUnmatchFatal: ", "red") + \
            "the type of the calling arg " + \
            colored(self.src_type, "magenta") + \
            " is not matched with the target function arg " + \
            colored(self.tgt_type, "magenta")

class IRedecFatal(EFatal):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return colored("ReDeclaredFatal: ", "red") + \
            "identifier " + \
            colored(self.name, "magenta") + \
            " has already been declared"

class IUndecFatal(EFatal):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return colored("UnDeclaredFatal: ", "red") + \
            "identifier " + \
            colored(self.name, "magenta") + \
            " was referenced before declared"

class EUnhandledError(EError):
    def __init__(self, msg):
        self.name = msg
    def __str__(self):
        return colored("UnexpectedError: ", "red") + msg

class IRedecError(EError):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return colored("ReDeclaredError: ", "red") + \
            "identifier " + \
            colored(self.name, "magenta") + \
            " has already been declared"

class IUndecError(EError):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return colored("UnDeclaredError: ", "red") + \
            "identifier " + \
            colored(self.name, "magenta") + \
            " was referenced before declared"
        

class TCastError(EError):
    def __init__(self, src_type: str, tgt_type: str):
        self.src_type = src_type
        self.tgt_type = tgt_type
    def __str__(self):
        return colored("TypeCastingError: ", "red") + \
            "unable to cast from " + \
            colored(self.src_type, "magenta") + " to " + \
            colored(self.tgt_type, "magenta")

class TMismatchError(EError):
    def __init__(self, src_type: str, tgt_type: str):
        self.src_type = src_type
        self.tgt_type = tgt_type
    def __str__(self):
        return colored("TypeMatchingError: ", "red") + \
            "unable to match " + \
            colored(self.src_type, "magenta") + " with " + \
            colored(self.tgt_type, "magenta")

class TImplicitCastWarning(EWarning):
    def __init__(self, src_type: str, tgt_type: str):
        self.src_type = src_type
        self.tgt_type = tgt_type    
    def __str__(self):
        return colored("ImplicitTypeCastingWarning: ", "yellow") + \
            "implicit type casting from " + \
            colored(self.src_type, "green") + " to " + \
            colored(self.tgt_type, "green")

class IGlobalNotInitWarning(EWarning):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return colored("GlobalVariableNotInitializedWarning: ", "yellow") + \
            "global variable " + \
            colored(self.name, "green") + \
            " is not initialized when declared"

class IFuncExitWarning(EWarning):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return colored("IFuncExitWarning: ", "yellow") + \
            "function " + \
            colored(self.name, "green") + \
            " does not has explicit exit"


if __name__ == "__main__":
    e = IRedecError('sum')
    print(e)
    e = IUndecError('sum')
    print(e)
    e = TCastError('i32*', 'i32')
    print(e)
    e = TMismatchError('i1', 'i32')
    print(e)
    e = TImplicitCastWarning('i1', 'i32')
    print(e)
    e = IGlobalNotInitWarning('sum')
    print(e)