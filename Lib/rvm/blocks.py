"Representation of a basic block."

import sys

from . import DISPATCH
from .instructions import Instruction

class Block:
    """represent a block of code with a single entry point (first instr)"""
    def __init__(self, block_type, parent, block_number):
        self.block_type = block_type
        self.parent = parent
        self.block_number = block_number
        self._address = -1      # -1 => needs updating...
        self.instructions = []
        self.stacklevel = -1

    def __str__(self):
        "useful summary"
        return (f"Block <{self.block_type}:{self.block_number}:{self.address}"
                f":{self.codelen()}:{len(self.instructions)}>")
    __repr__ = __str__

    @property
    def address(self):
        if self._address == -1:
            if self.block_number == 0:
                self._address = 0
            else:
                blocks = self.parent.blocks[self.block_type]
                prev_block = blocks[self.block_number - 1]
                assert self.block_type == prev_block.block_type
                # pylint: disable=protected-access
                self._address = prev_block.address + prev_block.codelen()
                self.parent.mark_dirty(self.block_number + 1)
        assert self._address %2 == 0, (self.block_number, self.codelen(),
                                       self._address)
        return self._address

    @address.setter
    def address(self, val):
        # Address of block number 0 must always be 0.
        self._address = 0 if self.block_number == 0 else val

    def display(self):
        offset = self.address
        for instr in self.instructions:
            print(f"{offset:4d} {instr}")
            offset += len(instr)

    def codelen(self):
        "Length of block converted to code bytes"
        return sum(len(instr) for instr in self.instructions)

    def set_stacklevel(self, level):
        if self.stacklevel != -1:
            if self.stacklevel == level:
                print("Warning: Setting stacklevel to", level,
                      "multiple times.", file=sys.stderr)
            else:
                raise ValueError(f"Already set stacklevel to {self.stacklevel} "
                                 f"for this block ({level})")
        else:
            self.stacklevel = level

    def append(self, instr):
        assert isinstance(instr, Instruction), instr
        self.instructions.append(instr)

    def __setitem__(self, i, instruction):
        self.instructions[i] = instruction

    def __getitem__(self, i):
        return self.instructions[i]

    def __delitem__(self, i):
        del self.instructions[i]

    def __len__(self):
        return len(self.instructions)

    def gen_rvm(self, rvm_block):
        "Populate RVM block with instructions converted from PyVM."
        rvm_block.instructions = []
        for pyvm_inst in self.instructions:
            try:
                convert = DISPATCH[pyvm_inst.opcode]
            except KeyError:
                print(f"No map for {pyvm_inst.opcode} ({pyvm_inst.name})")
                raise
            rvm_inst = convert(self.parent, pyvm_inst, rvm_block)
            if rvm_inst is None:
                # Attempt to translate unreachable code beyond
                # co_stacksize.  We are done with this block.
                break
            rvm_inst.line_number = pyvm_inst.line_number
            rvm_inst.index = len(rvm_block)
            #print(">>", rvm_inst)
            rvm_block.append(rvm_inst)

    def mark_dirty(self):
        "This block is dirty. Implicitly, so is everything downstream."
        self.parent.mark_dirty(self.block_number)

    def __bytes__(self):
        instr_bytes = []
        for instr in self.instructions:
            instr_bytes.append(bytes(instr))
        return b"".join(instr_bytes)
