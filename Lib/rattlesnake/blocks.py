"Representation of a basic block."

from rattlesnake.instructions import Instruction

class Block:
    """represent a block of code with a single entry point (first instr)"""
    def __init__(self, block_type):
        self.instructions = []
        self.stacklevel = -1
        self.address = -1
        self.block_number = -1
        self.block_type = block_type

    def __str__(self):
        "useful summary"
        return f"Block <{self.block_type}:{self.block_number}:{self.codelen()}>"

    def display(self):
        print(self)
        assert self.address >= 0
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

    def gen_rvm(self, isc):
        "Return a new block full of RVM instructions."
        new_block = Block("RVM")
        for pyvm_inst in self.instructions:
            convert = isc.dispatch[pyvm_inst.opcode]
            rvm_inst = convert(isc, pyvm_inst)
            new_block.append(rvm_inst)
        return new_block
