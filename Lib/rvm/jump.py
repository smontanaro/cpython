#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction
from .util import decode_oparg, EXT_ARG_OPCODE

def pop_jump(self, instr, block):
    "Jumps of various kinds"
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    opname = f"{opcode.opname[op]}_REG"[4:]
    self.set_block_stacklevel(oparg, self.top())
    return JumpIfInstruction(opcode.opmap[opname], block,
                             target=instr.target, source1=self.pop())
DISPATCH[opcode.opmap['POP_JUMP_IF_FALSE']] = pop_jump
DISPATCH[opcode.opmap['POP_JUMP_IF_TRUE']] = pop_jump

def jump_abs(self, instr, block):
    "Jumps of various kinds"
    op = instr.opcode
    # Reused unchanged from PyVM
    opname = f"{opcode.opname[op]}"
    return JumpAbsInstruction(opcode.opmap[opname], block,
                              target=instr.target)
DISPATCH[opcode.opmap['JUMP_FORWARD']] = jump_abs
DISPATCH[opcode.opmap['JUMP_ABSOLUTE']] = jump_abs

def return_(self, instr, block):
    "Jumps of various kinds"
    op = instr.opcode
    opname = f"{opcode.opname[op]}_REG"
    return ReturnInstruction(opcode.opmap[opname], block,
                             source1=self.pop())
DISPATCH[opcode.opmap['RETURN_VALUE']] = return_

class ReturnInstruction(Instruction):
    "RETURN_VALUE_REG"
    def __init__(self, op, block, **kwargs):
        self.populate(("source1",), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.source1,)

class JumpInstruction(Instruction):
    """Some kind of jump.

    Requires either a target (block number) or an address (offset from
    start of code block, target marked as unset).  If an address is
    given, it will be converted to a target block number later and
    deleted.

    """
    def __init__(self, op, block, **kwargs):
        if "target_address" in kwargs:
            self.populate(("target_address",), kwargs)
            self.target = -1    # unset so far
        else:
            # target block, not address
            self.populate(("target",), kwargs)
        super().__init__(op, block, **kwargs)

    def compute_relative_jump(self, target_block):
        "Compute relative jump to start of target_block."
        # Jump target is relative to the next instruction's address
        # target_block.address is an absolute address.  From that,
        # subtract this instruction's address, the address of the
        # current block plus the length of all instructions preceding
        # this one in the block.
        preceding_insts = self.block.instructions[:self.index]
        if preceding_insts:
            my_rel_addr = sum(len(inst) for inst in preceding_insts)
        else:
            my_rel_addr = 0
        jumpby = (target_block.address -
                  (self.block.address + my_rel_addr + len(self)))
        # Jump offsets are always two bytes
        return decode_oparg(jumpby, minimize=False)[-2:]

class JumpIfInstruction(JumpInstruction):
    "Specialized behavior for JUMP_IF_(TRUE|FALSE)_REG."
    def __init__(self, op, block, **kwargs):
        # register with comparison output
        self.populate(("source1",), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        """Return target block converted to address, plus src register."""
        isc = self.block.parent
        target_block = isc.blocks[self.block.block_type][self.target]
        addr_arg = decode_oparg(target_block.address)
        result = addr_arg + (self.source1,)
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
        return 6                # EXT_ARG, EXT_ARG, INSTR

    def __bytes__(self):
        # Since we assume two EXT_ARGS instructions in __len__, we
        # have to force it here as well, even if the eventual jump
        # address is < 256.
        code = []
        opargs = self.opargs
        if len(opargs) == 2:
            opargs = (0,) + opargs
        code.append(EXT_ARG_OPCODE)
        code.append(opargs[0])
        code.append(EXT_ARG_OPCODE)
        code.append(opargs[1])
        code.append(self.opcode)
        code.append(opargs[2])
        return bytes(code)


class JumpAbsInstruction(JumpInstruction):
    "Specialized behavior for JUMP_IF_ABSOLUTE_REG."
    @property
    def opargs(self):
        """Return target block converted to address, plus src register."""
        isc = self.block.parent
        target_block = isc.blocks[self.block.block_type][self.target]
        addr_arg = decode_oparg(target_block.address)
        result = addr_arg
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
        return 4                # EXT_ARG, INSTR

    def __bytes__(self):
        # Since we assume one EXT_ARG instruction in __len__, we have
        # to force it here as well, even if the eventual jump address
        # is < 256.
        code = []
        opargs = self.opargs
        while len(opargs) < 2:
            opargs = (0,) + opargs
        code.append(EXT_ARG_OPCODE)
        code.append(opargs[0])
        code.append(self.opcode)
        code.append(opargs[1])
        return bytes(code)
