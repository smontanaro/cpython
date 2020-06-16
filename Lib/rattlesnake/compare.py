#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

def compare(self, instr, block):
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    cmpop = oparg
    src2 = self.pop()
    src1 = self.pop()
    dst = self.push()
    return CompareOpInstruction(opcode.opmap['COMPARE_OP_REG'],
                                block,
                                dest=dst, source1=src1,
                                source2=src2, compare_op=cmpop)
DISPATCH[opcode.opmap['COMPARE_OP']] = compare

class CompareOpInstruction(Instruction):
    "Specialized behavior for COMPARE_OP_REG."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "source1", "compare_op", "source2"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1, self.source2, self.compare_op)
