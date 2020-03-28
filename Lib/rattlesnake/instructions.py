"Individual instructions."

from rattlesnake import opcodes

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

    EXT_ARG_OPCODE = opcodes.ISET.opmap["EXTENDED_ARG"]

    def __init__(self, opcode, opargs=(0,)):
        assert isinstance(opargs, tuple)
        self.opcode = opcode
        self.opargs = opargs
        self.expanded_opargs = ()

    def name(self):
        "human-readable name for the opcode"
        return opcodes.ISET.opname[self.opcode]

    def __len__(self):
        "Compute byte length of instruction."
        # In wordcode, an instruction is op, arg, each taking one
        # byte. If we have more than zero or one arg, we use
        # EXTENDED_ARG instructions to carry the other args, each
        # again two bytes.
        opargs = self.expanded_opargs or self.opargs
        return 2 + 2 * len(opargs[1:])

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

    def source_registers(self):
        "Return a tuple of all source registers."
        return ()

    def dest_registers(self):
        "Return a tuple of all destination registers."
        # Tuple returned for consistency. Empty tuple is default.
        return ()

    def first(self):
        "Everything preceding the dest register."
        return ()

    def rest(self):
        "Everything else."
        return self.opargs

    def update_opargs(self, first=(), source=(), dest=(), rest=()):
        if not first:
            first = self.first()
        if not source:
            source = self.source_registers()
        if not dest:
            dest = self.dest_registers()
        if not rest:
            rest = self.rest()
        self.opargs = first + dest + source + rest

    def update_expanded_opargs(self, first=(), source=(), dest=(), rest=()):
        "clunky way to create an opargs with expanded jump targets, etc"
        # TBD: Need to improve this!
        save_opargs = self.opargs
        self.update_opargs(first, source, dest, rest)
        self.expanded_opargs = self.opargs
        self.opargs = save_opargs

    def to_bytes(self, address, block_to_address):
        "to_bytes when target address calculation isn't required."
        result = []
        n_ext_arg = 0
        opargs = self.expanded_opargs or self.opargs
        for arg in opargs[:-1]:
            result.extend([self.EXT_ARG_OPCODE, arg])
        result.extend([self.opcode, opargs[-1]])
        try:
            return bytes(result)
        except TypeError:
            print(result)
            raise

class JumpInstruction(Instruction):
    "Some kind of jump."
    def split_target(self, target):
        "Maybe extendify a too large target address."
        split = []
        while target:
            split.insert(0, target & 0xff)
            target >>= 8
        return tuple(split)

class JumpIfInstruction(JumpInstruction):
    "Specialized behavior for JUMP_IF_(TRUE|FALSE)_REG."
    def first(self):
        return self.opargs[0:1]

    def source_registers(self):
        return self.opargs[1:2]

    def rest(self):
        return ()

    def jump_target(self):
        "Jump target as block number."
        return self.first()[0]

    def to_bytes(self, address, block_to_address):
        "Target address calculation, then basic byte string gen."
        target = block_to_address[self.jump_target()]
        self.update_expanded_opargs(first=self.split_target(target))
        return super().to_bytes(address, block_to_address)

class LoadFastInstruction(Instruction):
    "Specialized behavior for LOAD_FAST_REG."
    def source_registers(self):
        return self.opargs[1:2]

    def dest_registers(self):
        return self.opargs[0:1]

    def rest(self):
        return ()

# SFI and LFI are really the same instruction. We distinguish only to
# avoid mistakes using isinstance. There is probably a cleaner way to
# do this, but this code duplication suffices for the moment.
class StoreFastInstruction(Instruction):
    "Specialized behavior for STORE_FAST_REG."
    def source_registers(self):
        return self.opargs[1:2]

    def dest_registers(self):
        return self.opargs[0:1]

    def rest(self):
        return ()

class CompareOpInstruction(Instruction):
    "Specialized behavior for COMPARE_OP_REG."
    def source_registers(self):
        return self.opargs[1:3]

    def dest_registers(self):
        return self.opargs[0:1]

    def rest(self):
        return self.opargs[3:]

class BinOpInstruction(Instruction):
    "Specialized behavior for binary operations."
    def source_registers(self):
        return self.opargs[1:3]

    def dest_registers(self):
        return self.opargs[0:1]

    def rest(self):
        return ()

class NOPInstruction(Instruction):
    "Just easier this way..."

class LoadGlobalInstruction(Instruction):
    "LOAD_GLOBAL_REG"
    def dest_registers(self):
        return self.opargs[0:1]

    def rest(self):
        return self.opargs[1:2]
