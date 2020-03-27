"Individual instructions."

import regopcodes as opcodes

class Instruction:
    """Represent an instruction in either PyVM or RVM.

    Instruction opargs are currently represented by a tuple. It
    consists of up to four parts:

    * first - anything before the destination register
    * dest - destination register
    * sources - source registers
    * rest - anything after the source registers

    Any or all of these fields may be empty. By default, the first
    three are considered empty and the rest is all
    elements. EXTENDED_ARG needs no special treatment, so is created
    as an instance of Instruction. Other subclasses carve up opargs in
    different ways. CompareOpInstruction has a dest, two sources and a
    comparison operator (rest), but no first. JumpIfInstruction has
    first (the target block number) and a source (destination register
    of the previous COMPARE_OP instruction, but no dest or rest
    elements. The update_opargs method is used to update any piece of
    opargs.

    """
    def __init__(self, opcode, opargs=(0,)):
        assert isinstance(opargs, tuple)
        self.opcode = opcode
        self.opargs = opargs

    def name(self):
        "human-readable name for the opcode"
        return opcodes.ISET.opname[self.opcode]

    def __len__(self):
        "Compute byte length of instruction."
        # In wordcode, an instruction is op, arg, each taking one
        # byte. If we have more than zero or one arg, we use
        # EXTENDED_ARG instructions to carry the other args, each
        # again two bytes.
        return 2 + 2 * len(self.opargs[1:])

    def __str__(self):
        return f"Instruction({self.name()}, {self.opargs})"

    def is_abs_jump(self):
        "True if opcode is an absolute jump."
        return self.opcode in opcodes.ISET.abs_jumps

    def is_rel_jump(self):
        "True if opcode is a relative jump."
        return self.opcode in opcodes.ISET.rel_jumps

    def is_jump(self):
        return self.is_abs_jump() or self.is_rel_jump()

    def get_source_registers(self):
        "Return a tuple of all source registers."
        return ()

    def get_dest_registers(self):
        "Return a tuple of all destination registers."
        # Tuple returned for consistency. Empty tuple is default.
        return ()

    def get_first(self):
        "Everything preceding the dest register."
        return ()

    def get_rest(self):
        "Everything else."
        return self.opargs

    def update_opargs(self, first=(), sources=(), dest=(), rest=()):
        if not first:
            first = self.get_first()
        if not sources:
            sources = self.get_source_registers()
        if not dest:
            dest = self.get_dest_registers()
        if not rest:
            rest = self.get_rest()
        self.opargs = first + dest + sources + rest

class JumpIfInstruction(Instruction):
    "Specialized behavior for JUMP_IF_(TRUE|FALSE)_REG."
    def get_first(self):
        return self.opargs[0:1]

    def get_source_registers(self):
        return self.opargs[1:2]

    def get_rest(self):
        return ()

class LoadFastInstruction(Instruction):
    "Specialized behavior for LOAD_FAST_REG."
    def get_source_registers(self):
        return self.opargs[1:2]

    def get_dest_registers(self):
        return self.opargs[0:1]

    def get_rest(self):
        return ()

# SFI and LFI are really the same instruction. We distinguish only to
# avoid mistakes using isinstance. There is probably a cleaner way to
# do this, but this code duplication suffices for the moment.
class StoreFastInstruction(Instruction):
    "Specialized behavior for STORE_FAST_REG."
    def get_source_registers(self):
        return self.opargs[1:2]

    def get_dest_registers(self):
        return self.opargs[0:1]

    def get_rest(self):
        return ()

class CompareOpInstruction(Instruction):
    "Specialized behavior for COMPARE_OP_REG."
    def get_source_registers(self):
        return self.opargs[1:3]

    def get_dest_registers(self):
        return self.opargs[0:1]

    def get_rest(self):
        return self.opargs[3:]

class BinOpInstruction(Instruction):
    "Specialized behavior for binary operations."
    def get_source_registers(self):
        return self.opargs[1:3]

    def get_dest_registers(self):
        return self.opargs[0:1]

    def get_rest(self):
        return ()

class NOPInstruction(Instruction):
    "Just easier this way..."

class LoadGlobalInstruction(Instruction):
    "LOAD_GLOBAL_REG"
    def get_dest_registers(self):
        return self.opargs[0:1]

    def get_rest(self):
        return self.opargs[1:2]
