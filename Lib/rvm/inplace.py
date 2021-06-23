#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

def inplace_op(self, instr, block):
    "src1 <- src1 OP src2"
    opname = "%s_REG" % opcode.opname[instr.opcode]
    src2 = self.pop()       # right-hand register src
    src1 = self.top()       # left-hand register src & output
    return InplaceOpInstruction(opcode.opmap[opname], block,
                                source1=src1, source2=src2)
DISPATCH[opcode.opmap['INPLACE_POWER']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_MULTIPLY']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_MATRIX_MULTIPLY']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_TRUE_DIVIDE']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_FLOOR_DIVIDE']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_MODULO']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_ADD']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_SUBTRACT']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_LSHIFT']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_RSHIFT']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_AND']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_XOR']] = inplace_op
DISPATCH[opcode.opmap['INPLACE_OR']] = inplace_op

class InplaceOpInstruction(Instruction):
    "Specialized behavior for binary operations."
    def __init__(self, op, block, **kwargs):
        self.populate(("source1", "source2"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.source1, self.source2)
