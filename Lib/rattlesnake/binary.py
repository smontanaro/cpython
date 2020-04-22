#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

def bin_op(self, instr, block):
    "dst <- src1 OP src2"
    opname = "%s_REG" % opcode.opname[instr.opcode]
    ## TBD... Still not certain I have argument order/byte packing correct.
    src2 = self.pop()       # right-hand register src
    src1 = self.pop()       # left-hand register src
    dst = self.push()       # dst
    return BinOpInstruction(opcode.opmap[opname], block,
                            dest=dst, source1=src1, source2=src2)
DISPATCH[opcode.opmap['BINARY_POWER']] = bin_op
DISPATCH[opcode.opmap['BINARY_MULTIPLY']] = bin_op
DISPATCH[opcode.opmap['BINARY_MATRIX_MULTIPLY']] = bin_op
DISPATCH[opcode.opmap['BINARY_TRUE_DIVIDE']] = bin_op
DISPATCH[opcode.opmap['BINARY_FLOOR_DIVIDE']] = bin_op
DISPATCH[opcode.opmap['BINARY_MODULO']] = bin_op
DISPATCH[opcode.opmap['BINARY_ADD']] = bin_op
DISPATCH[opcode.opmap['BINARY_SUBTRACT']] = bin_op
DISPATCH[opcode.opmap['BINARY_LSHIFT']] = bin_op
DISPATCH[opcode.opmap['BINARY_RSHIFT']] = bin_op
DISPATCH[opcode.opmap['BINARY_AND']] = bin_op
DISPATCH[opcode.opmap['BINARY_XOR']] = bin_op
DISPATCH[opcode.opmap['BINARY_OR']] = bin_op
DISPATCH[opcode.opmap['BINARY_SUBSCR']] = bin_op
DISPATCH[opcode.opmap['INPLACE_POWER']] = bin_op
DISPATCH[opcode.opmap['INPLACE_MULTIPLY']] = bin_op
DISPATCH[opcode.opmap['INPLACE_MATRIX_MULTIPLY']] = bin_op
DISPATCH[opcode.opmap['INPLACE_TRUE_DIVIDE']] = bin_op
DISPATCH[opcode.opmap['INPLACE_FLOOR_DIVIDE']] = bin_op
DISPATCH[opcode.opmap['INPLACE_MODULO']] = bin_op
DISPATCH[opcode.opmap['INPLACE_ADD']] = bin_op
DISPATCH[opcode.opmap['INPLACE_SUBTRACT']] = bin_op
DISPATCH[opcode.opmap['INPLACE_LSHIFT']] = bin_op
DISPATCH[opcode.opmap['INPLACE_RSHIFT']] = bin_op
DISPATCH[opcode.opmap['INPLACE_AND']] = bin_op
DISPATCH[opcode.opmap['INPLACE_XOR']] = bin_op
DISPATCH[opcode.opmap['INPLACE_OR']] = bin_op

class BinOpInstruction(Instruction):
    "Specialized behavior for binary operations."
    def __init__(self, op, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.source2 = kwargs["source2"]
        del kwargs["source2"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1, self.source2)
