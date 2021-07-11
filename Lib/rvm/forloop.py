#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction
from .jump import JumpIfInstruction
from .util import EXT_ARG_OPCODE

def for_iter(self, instr, block):
    op = instr.opcode
    opname = "%s_REG" % opcode.opname[op]
    src = self.top()
    dst = self.push()
    return ForIterInstruction(opcode.opmap[opname], block,
                              dest=dst, source1=src,
                              target=instr.target)
DISPATCH[opcode.opmap['FOR_ITER']] = for_iter

def get_iter(self, instr, block):
    op = instr.opcode
    opname = "%s_REG" % opcode.opname[op]
    src = self.pop()
    dst = self.push()
    return GetIterInstruction(opcode.opmap[opname], block,
                              dest=dst, source1=src)
DISPATCH[opcode.opmap['GET_ITER']] = get_iter

class ForIterInstruction(JumpIfInstruction):
    "dest <- iter(source1) + jumpby"
    def __init__(self, op, block, **kwargs):
        self.populate(("dest",), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        """Return target block as address, plus dest and src registers."""
        isc = self.block.parent
        target_block = isc.blocks[self.block.block_type][self.target]
        jumpby = self.compute_relative_jump(target_block)
        result = (self.dest, self.source1) + jumpby
        if result != self._opargs:
            self._opargs = result
            self.block.mark_dirty()
        return result

    def __len__(self):
        # Short circuit the length calculation to avoid unbounded
        # recursion.  Suppose this instruction is in block N and has
        # block N+1 as a target.  To compute the target address of
        # block N+1 you need the length of block N, which needs the
        # lengths of all its instructions, which leads you back here
        # and you start chasing your tail.
        return 8                # EXT_ARG, EXT_ARG, EXT_ARG, INSTR

    def __bytes__(self):
        # Since we assume three EXT_ARGS instructions in __len__, we
        # have to force it here as well, even if any leading EXT_ARG
        # opargs == 0.
        code = []
        opargs = self.opargs
        while len(opargs) < 4:
            opargs = (0,) + opargs
        code.append(EXT_ARG_OPCODE)
        code.append(opargs[0])
        code.append(EXT_ARG_OPCODE)
        code.append(opargs[1])
        code.append(EXT_ARG_OPCODE)
        code.append(opargs[2])
        code.append(self.opcode)
        code.append(opargs[3])
        return bytes(code)

class GetIterInstruction(Instruction):
    "dest <- iter(source1)"
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "source1"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1)
