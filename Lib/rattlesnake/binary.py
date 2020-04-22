#!/usr/bin/env python3

import opcode

from rattlesnake import DISPATCH
from rattlesnake.instructions import BinOpInstruction

class BinOpMixin:
    def binary_convert(self, instr, block):
        "dst <- src1 OP src2"
        opname = "%s_REG" % opcode.opname[instr.opcode]
        ## TBD... Still not certain I have argument order/byte packing correct.
        src2 = self.pop()       # right-hand register src
        src1 = self.pop()       # left-hand register src
        dst = self.push()       # dst
        return BinOpInstruction(opcode.opmap[opname], block,
                                dest=dst, source1=src1, source2=src2)
    DISPATCH[opcode.opmap['BINARY_POWER']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_MULTIPLY']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_MATRIX_MULTIPLY']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_TRUE_DIVIDE']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_FLOOR_DIVIDE']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_MODULO']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_ADD']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_SUBTRACT']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_LSHIFT']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_RSHIFT']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_AND']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_XOR']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_OR']] = binary_convert
    DISPATCH[opcode.opmap['BINARY_SUBSCR']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_POWER']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_MULTIPLY']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_MATRIX_MULTIPLY']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_TRUE_DIVIDE']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_FLOOR_DIVIDE']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_MODULO']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_ADD']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_SUBTRACT']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_LSHIFT']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_RSHIFT']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_AND']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_XOR']] = binary_convert
    DISPATCH[opcode.opmap['INPLACE_OR']] = binary_convert
