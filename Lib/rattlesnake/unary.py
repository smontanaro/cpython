#!/usr/bin/env python3

import opcode

from rattlesnake import DISPATCH
from rattlesnake.instructions import UnaryOpInstruction

class UnaryMixin:
    "Unary operator mixin class"

    def unary_convert(self, instr, block):
        opname = "%s_REG" % opcode.opname[instr.opcode]
        src = self.pop()
        dst = self.push()
        return UnaryOpInstruction(opcode.opmap[opname], block,
                                  dest=dst, source1=src)
    DISPATCH[opcode.opmap['UNARY_INVERT']] = unary_convert
    DISPATCH[opcode.opmap['UNARY_POSITIVE']] = unary_convert
    DISPATCH[opcode.opmap['UNARY_NEGATIVE']] = unary_convert
    DISPATCH[opcode.opmap['UNARY_NOT']] = unary_convert
