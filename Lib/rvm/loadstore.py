#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction
from .util import StackSizeException

def load_fast(self, instr, block):
    "loads of various kinds"
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    src = oparg         # offset into localsplus
    try:
        dst = self.push()
    except StackSizeException:
        # unreachable code - stop translating
        return None
    opname = f"{opcode.opname[op]}_REG"
    return LoadFastInstruction(opcode.opmap[opname], block,
                               dest=dst, source1=src)
DISPATCH[opcode.opmap['LOAD_FAST']] = load_fast

def load_const(self, instr, block):
    #print("block:", block)
    #print("instr:", instr)
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    src = oparg             # offset into localsplus
    try:
        dst = self.push()
    except StackSizeException:
        # unreachable code - stop translating
        return None
    opname = f"{opcode.opname[op]}_REG"
    return LoadConstInstruction(opcode.opmap[opname], block,
                                dest=dst, name1=src)
DISPATCH[opcode.opmap['LOAD_CONST']] = load_const

def load_named(self, instr, block):
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    src = oparg             # offset into names tuple or freevars array
    try:
        dst = self.push()
    except StackSizeException:
        # unreachable code - stop translating
        return None
    opname = f"{opcode.opname[op]}_REG"
    return LoadGlobalInstruction(opcode.opmap[opname], block,
                                 dest=dst, name1=src)
DISPATCH[opcode.opmap['LOAD_GLOBAL']] = load_named
DISPATCH[opcode.opmap['LOAD_DEREF']] = load_named

def store_fast(self, instr, block):
    "stores of various kinds"
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    opname = f"{opcode.opname[op]}_REG"
    dst = oparg
    src = self.pop()
    return StoreFastInstruction(opcode.opmap[opname], block,
                                dest=dst, source1=src)
DISPATCH[opcode.opmap['STORE_FAST']] = store_fast

def store_global(self, instr, block):
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    opname = f"{opcode.opname[op]}_REG"
    name1 = oparg
    src = self.pop()
    return StoreGlobalInstruction(opcode.opmap[opname], block,
                                  name1=name1, source1=src)
DISPATCH[opcode.opmap['STORE_GLOBAL']] = store_global


class LoadFastInstruction(Instruction):
    "Specialized behavior for fast loads."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "source1"), kwargs)
        super().__init__(op, block, **kwargs)
        # Used during forward propagation
        self.protected = False

    @property
    def opargs(self):
        #print(f">> {self.name}.opargs:", (self.dest, self.source1))
        return (self.dest, self.source1)

# SFI and LFI are really the same instruction. We distinguish only to
# avoid mistakes using isinstance. There is probably a cleaner way to
# do this, but this code duplication suffices for the moment.
class StoreFastInstruction(Instruction):
    "Specialized behavior for fast stores."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "source1"), kwargs)
        super().__init__(op, block, **kwargs)
        # (Might be) used during backward propagation
        self.protected = False

    @property
    def opargs(self):
        return (self.dest, self.source1)

class LoadGlobalInstruction(Instruction):
    "dst <- global name"
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "name1"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.name1)

class LoadConstInstruction(Instruction):
    "dst <- constant"
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "name1"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.name1)

class StoreGlobalInstruction(Instruction):
    "Specialized behavior for stores."
    def __init__(self, op, block, **kwargs):
        self.populate(("name1", "source1"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.name1, self.source1)

    # def subscript_convert(self, instr, block):
    #     op = instr.opcode
    #     if op == opcode.opmap['STORE_SUBSCR']:
    #         index = self.pop()
    #         obj = self.pop()
    #         val = self.pop()
    #         return Instruction(opcode.opmap['STORE_SUBSCR_REG'],
    #                            (obj, index, val))
    #     if op == opcode.opmap['DELETE_SUBSCR']:
    #         index = self.pop()
    #         obj = self.pop()
    #         return Instruction(opcode.opmap['DELETE_SUBSCR_REG'],
    #                            (obj, index))
    #     raise ValueError(f"Unhandled opcode {opcode.opname[op]}")
    # DISPATCH[opcode.opmap['STORE_SUBSCR']] = subscript_convert
    # DISPATCH[opcode.opmap['DELETE_SUBSCR']] = subscript_convert
