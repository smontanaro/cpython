#!/usr/bin/env python3

import opcode
import sys

from . import DISPATCH
from .instructions import Instruction

def raise_varargs(self, instr, block):
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    cause = exc = None
    if oparg == 2:
        cause = self.pop()
        exc = self.pop()
    if oparg == 1:
        exc = self.pop()
    return RaiseVarargsInstruction(opcode.opmap['RAISE_VARARGS_REG'], block,
                                   cause=cause, exc=exc, what=oparg)
DISPATCH[opcode.opmap['RAISE_VARARGS']] = raise_varargs

class RaiseVarargsInstruction(Instruction):
    "Specialized behavior for RAISE_VARARGS_REG."
    def __init__(self, op, block, **kwargs):
        self.populate(("cause", "exc", "what"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.cause, self.exc, self.what)
