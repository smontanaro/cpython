"Representation of a basic block."

from rattlesnake.instructions import Instruction

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
        return f"Block <{self.block_type}:{self.block_number}:{self.address}:{self.codelen()}>"

    @property
    def address(self):
        if self._address == -1:
            blocks = self.parent.blocks[self.block_type]
            prev_block = blocks[self.block_number - 1]
            assert self.block_type == prev_block.block_type
            # pylint: disable=protected-access
            self._address = prev_block._address + prev_block.codelen()
            self.parent.mark_dirty(self.block_number + 1)
        assert self._address != -1
        return self._address

    @address.setter
    def address(self, val):
        self._address = val

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
                print("Warning: Setting stacklevel to", level, end=' ')
                print("multiple times.")
            else:
                raise ValueError(f"Already set stacklevel to {self.stacklevel} "
                                 "for this block")
        else:
            self.stacklevel = level

    def append(self, instr):
        assert isinstance(instr, Instruction), instr
        self.instructions.append(instr)

    def extend(self, instructions):
        for instruction in instructions:
            self.append(instruction)

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
            convert = self.parent.dispatch[pyvm_inst.opcode]
            rvm_inst = convert(self.parent, pyvm_inst, rvm_block)
            rvm_inst.line_number = pyvm_inst.line_number
            rvm_block.append(rvm_inst)

    def mark_dirty(self):
        "This block is dirty. Implicitly, so is everything downstream."
        self.parent.mark_dirty(self.block_number)

    def __bytes__(self):
        instr_bytes = []
        for instr in self.instructions:
            instr_bytes.append(bytes(instr))
        return b"".join(instr_bytes)
