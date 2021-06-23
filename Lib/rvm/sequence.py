#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

def build_sequence(self, instr, block):
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    opname = "%s_REG" % opcode.opname[op]
    eltlen = 2 if op == opcode.opmap['BUILD_MAP'] else 1
    n = oparg
    for _ in range(n * eltlen):
        self.pop()
    dst = self.push()
    #print(f">>> dst: {dst}, len: {n}")
    return BuildSeqInstruction(opcode.opmap[opname], block,
                               length=n, dest=dst)
DISPATCH[opcode.opmap['BUILD_TUPLE']] = build_sequence
DISPATCH[opcode.opmap['BUILD_LIST']] = build_sequence
DISPATCH[opcode.opmap['BUILD_MAP']] = build_sequence
DISPATCH[opcode.opmap['BUILD_SET']] = build_sequence
DISPATCH[opcode.opmap['BUILD_STRING']] = build_sequence

def extend_sequence(self, instr, block):
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    opname = "%s_REG" % opcode.opname[op]
    src = self.pop()
    dst = self.peek(oparg)
    return ExtendSeqInstruction(opcode.opmap[opname], block,
                                source1=src, dest=dst)
DISPATCH[opcode.opmap['LIST_EXTEND']] = extend_sequence


class BuildSeqInstruction(Instruction):
    "Specialized behavior for sequence construction operations."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "length"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.length)

class ExtendSeqInstruction(Instruction):
    "Specialized behavior for LIST_EXTEND operation."
    # dest is modified in-place.
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "source1"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1)
