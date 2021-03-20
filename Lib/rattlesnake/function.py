
import opcode

from . import DISPATCH
from .instructions import Instruction

def function(self, instr, block):
    "dst <- function(...)"
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    nargs = oparg
    dest = self.top() - nargs
    for _ in range(nargs):
        _x = self.pop()
    return CallInstruction(opcode.opmap['CALL_FUNCTION_REG'],
                           block, nargs=nargs, dest=dest)
DISPATCH[opcode.opmap['CALL_FUNCTION']] = function

def function_kw(self, instr, block):
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    nargs = oparg
    nreg = self.top()
    dest = self.top() - nargs - 1
    #print(nargs, nreg, dest)
    for _ in range(nargs + 1):
        _x = self.pop()
    return CallInstructionKW(opcode.opmap['CALL_FUNCTION_KW_REG'],
                             block, nargs=nargs, nreg=nreg, dest=dest)
DISPATCH[opcode.opmap['CALL_FUNCTION_KW']] = function_kw

def function_ex(self, instr, block):
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    nargs = oparg
    kwargs = None
    if oparg & 0x01:
        kwargs = self.pop()
    cargs = self.pop()
    func = self.top()
    print(kwargs, cargs, func)
    return CallInstructionEX(opcode.opmap['CALL_FUNCTION_EX_REG'],
                             block, kwargs_=kwargs, cargs=cargs, func=func)
DISPATCH[opcode.opmap['CALL_FUNCTION_EX']] = function_ex

def load_method(self, instr, block):
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    obj = self.top()
    return LoadMethodInstruction(opcode.opmap['LOAD_METHOD_REG'],
                                 block, dest=obj, name1=obj)
DISPATCH[opcode.opmap['LOAD_METHOD']] = load_method

class CallInstruction(Instruction):
    "Basic CALL_FUNCTION_REG."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "nargs"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.nargs)

class CallInstructionKW(Instruction):
    "Basic CALL_FUNCTION_KW_REG."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "nargs", "nreg"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.nreg, self.nargs)

class CallInstructionEX(Instruction):
    "CALL_FUNCTION_EX_REG."
    def __init__(self, op, block, **kwargs):
        self.populate(("kwargs_", "cargs", "func"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.kwargs_, self.cargs, self.func)

class LoadMethodInstruction(Instruction):
    "LOAD_METHOD_REG."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "name1"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.name1)
