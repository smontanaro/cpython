#!/usr/bin/env python3

import opcode

from rattlesnake import DISPATCH
from rattlesnake.instructions import Instruction

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
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.source2 = kwargs["source2"]
        del kwargs["source2"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        self.compare_op = kwargs["compare_op"]
        del kwargs["compare_op"]
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1, self.source2, self.compare_op)
