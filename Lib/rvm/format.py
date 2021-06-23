#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

# Nicked from Include/ceval.h
FVC_MASK = 0x3
FVC_NONE = 0x0
FVC_STR = 0x1
FVC_REPR = 0x2
FVC_ASCII = 0x3
FVS_MASK = 0x4
FVS_HAVE_SPEC = 0x4

def build_format_value(self, instr, block):
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    opname = "FORMAT_VALUE_REG"
    # oparg codes for two features. The first two bits identify one of
    # four converter (str, repr, ascii or nothing). The third bit
    # identifies whether or not there is a formatting spec.  The two
    # are mutually exclusive, specs being introduced by ":",
    # converters being introduced by "!".
    have_spec = oparg & FVS_MASK
    converter = oparg & FVC_MASK

    # If there is a spec, it's the top of the stack.
    if have_spec:
        fmt_spec = self.pop()
    else:
        fmt_spec = 0

    # The value is the next spot on the stack
    value = self.pop()
    # Which gets replaced by the result of the format operation
    dst = self.push()
    return BuildFormatInstruction(opcode.opmap[opname], block,
                                  dest=dst, flags=(have_spec | converter), source1=value,
                                  spec=fmt_spec)
DISPATCH[opcode.opmap['FORMAT_VALUE']] = build_format_value

class BuildFormatInstruction(Instruction):
    "Specialized behavior for FORMAT_VALUE."
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "source1", "spec", "flags"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1, self.spec, self.flags)
