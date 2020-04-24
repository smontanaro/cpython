#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

def load_attr(self, instr, block):
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    src = self.pop()
    attr = oparg
    dst = self.push()
    return LoadAttrInstruction(opcode.opmap['LOAD_ATTR_REG'], block,
                               dest=dst, source1=src, attr=attr)

def store_attr(self, instr, block):
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    src1 = self.pop()
    attr = oparg
    src2 = self.pop()
    return StoreAttrInstruction(opcode.opmap['STORE_ATTR_REG'], block,
                                source1=src1, attr=attr, source2=src2)

def del_attr(self, instr, block):
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    src = self.pop()
    attr = oparg
    return DelAttrInstruction(opcode.opmap['DELETE_ATTR_REG'], block,
                              source1=src, attr=attr)

DISPATCH[opcode.opmap['STORE_ATTR']] = store_attr
DISPATCH[opcode.opmap['DELETE_ATTR']] = del_attr
DISPATCH[opcode.opmap['LOAD_ATTR']] = load_attr

class LoadAttrInstruction(Instruction):
    "dest <- source1.attr"
    # dest and source1 are registers, attr is an offset into names
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "source1", "attr"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1, self.attr)

class StoreAttrInstruction(Instruction):
    "source1.attr <- source2"
    # source1 and source2 are registers, attr is an offset into names
    def __init__(self, op, block, **kwargs):
        self.populate(("source1", "attr", "source2"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.source1, self.attr, self.source2)

class DelAttrInstruction(Instruction):
    "del source1.attr"
    # source1 is a register, attr is an offset into names
    def __init__(self, op, block, **kwargs):
        self.populate(("source1", "attr"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.source1, self.attr)
