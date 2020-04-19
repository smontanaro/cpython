"""Individual instructions.

Each Instruction object has an opcode (a fixed integer) and both name
and opargs attributes which are implemented as properties. They
reference back to the block where they are defined (again, a fixed
attribute). In addition, various Instruction subclasses may implement
other attributes needed for specialized tasks. For example, jump
instructions need to calculate addresses (relative or absolute) which
will depend on their enclosing block's address.

"""

from rattlesnake import opcodes
from rattlesnake.util import decode_oparg

class Instruction:
    """Represent an instruction in either PyVM or RVM.

    Instruction opargs are currently represented by a tuple. Its
    makeup varies by Instruction subclass.

    """

    EXT_ARG_OPCODE = opcodes.ISET.opmap["EXTENDED_ARG"]

    def __init__(self, opcode, block, **kwargs):
        self.opcode = opcode
        self._opargs = (0,)
        self.block = block
        # unset (or same as previous instruction?)
        self.line_number = -1
        if kwargs:
            raise ValueError(f"Non-empty kwargs at top level {kwargs}")

    @property
    def name(self):
        "Human-readable name for the opcode."
        return opcodes.ISET.opname[self.opcode]

    @property
    def opargs(self):
        """Overrideable property

        opargs will be composed of different bits for different instructions.
        """
        return self._opargs

    def __len__(self):
        "Compute byte length of instruction."
        # In wordcode, an instruction is op, arg, each taking one
        # byte. If we have more than zero or one arg, we use
        # EXTENDED_ARG instructions to carry the other args, each
        # again two bytes.
        return 2 + 2 * len(self.opargs[1:])

    def __str__(self):
        return f"Instruction({self.line_number}: {self.name}, {self.opargs})"

    def is_abs_jump(self):
        "True if opcode is an absolute jump."
        return self.opcode in opcodes.ISET.abs_jumps

    def is_rel_jump(self):
        "True if opcode is a relative jump."
        return self.opcode in opcodes.ISET.rel_jumps

    def is_jump(self):
        "True for any kind of jump."
        return self.is_abs_jump() or self.is_rel_jump()

    def __bytes__(self):
        "Generate wordcode."
        code = []
        for arg in self.opargs[:-1]:
            code.append(self.EXT_ARG_OPCODE)
            code.append(arg)
        code.append(self.opcode)
        code.append(self.opargs[-1])
        return bytes(code)

class PyVMInstruction(Instruction):
    "For basic PyVM instructions."
    def __init__(self, opcode, block, **kwargs):
        opargs = kwargs["opargs"]
        del kwargs["opargs"]
        super().__init__(opcode, block, **kwargs)
        self._opargs = opargs

class JumpInstruction(Instruction):
    """Some kind of jump.

    Requires either a target (block number) or an address (offset from
    start of code block, target marked as unset).  If an address is
    given, it will be converted to a target block number later and
    deleted.

    """
    def __init__(self, opcode, block, **kwargs):
        if "address" in kwargs:
            self.target_address = kwargs["address"]
            del kwargs["address"]
            self.target = -1    # unset so far
        else:
            # target block, not address
            self.target = kwargs["target"]
            del kwargs["target"]
        super().__init__(opcode, block, **kwargs)

class JumpIfInstruction(JumpInstruction):
    "Specialized behavior for JUMP_IF_(TRUE|FALSE)_REG."
    def __init__(self, opcode, block, **kwargs):
        # register with comparison output
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        super().__init__(opcode, block, **kwargs)

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
        code.append(self.EXT_ARG_OPCODE)
        code.append(opargs[0])
        code.append(self.EXT_ARG_OPCODE)
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
        code.append(self.EXT_ARG_OPCODE)
        code.append(opargs[0])
        code.append(self.opcode)
        code.append(opargs[1])
        return bytes(code)

class CallInstruction(Instruction):
    "Basic CALL_FUNCTION_REG."
    def __init__(self, opcode, block, **kwargs):
        self.nargs = kwargs["nargs"]
        del kwargs["nargs"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.nargs)

class CallInstructionKW(Instruction):
    "Basic CALL_FUNCTION_KW_REG."
    def __init__(self, opcode, block, **kwargs):
        self.nargs = kwargs["nargs"]
        del kwargs["nargs"]
        self.nreg = kwargs["nreg"]
        del kwargs["nreg"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.nreg, self.nargs)

class LoadFastInstruction(Instruction):
    "Specialized behavior for fast loads."
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)
        # Used during forward propagation
        self.protected = False

    @property
    def opargs(self):
        return (self.dest, self.source1)

# SFI and LFI are really the same instruction. We distinguish only to
# avoid mistakes using isinstance. There is probably a cleaner way to
# do this, but this code duplication suffices for the moment.
class StoreFastInstruction(Instruction):
    "Specialized behavior for fast stores."
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)
        # (Might be) used during backward propagation
        self.protected = False

    @property
    def opargs(self):
        return (self.dest, self.source1)

class LoadGlobalInstruction(Instruction):
    def __init__(self, opcode, block, **kwargs):
        self.name1 = kwargs["name1"]
        del kwargs["name1"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.name1)

class LoadConstInstruction(Instruction):
    def __init__(self, opcode, block, **kwargs):
        self.name1 = kwargs["name1"]
        del kwargs["name1"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.name1)

class StoreGlobalInstruction(Instruction):
    "Specialized behavior for stores."
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.name1 = kwargs["name1"]
        del kwargs["name1"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.name1, self.source1)

class CompareOpInstruction(Instruction):
    "Specialized behavior for COMPARE_OP_REG."
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.source2 = kwargs["source2"]
        del kwargs["source2"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        self.compare_op = kwargs["compare_op"]
        del kwargs["compare_op"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1, self.source2, self.compare_op)

class BinOpInstruction(Instruction):
    "Specialized behavior for binary operations."
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.source2 = kwargs["source2"]
        del kwargs["source2"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1, self.source2)

class UnaryOpInstruction(Instruction):
    "Specialized behavior for unary operations."
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1)

class UnaryOpInstruction(Instruction):
    "Specialized behavior for unary operations."
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1)

class BuildSeqInstruction(Instruction):
    "Specialized behavior for sequence construction operations."
    def __init__(self, opcode, block, **kwargs):
        self.length = kwargs["length"]
        del kwargs["length"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.length)

class ExtendSeqInstruction(Instruction):
    "Specialized behavior for LIST_EXTEND operation."
    # dest is modified in-place.
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        self.dest = kwargs["dest"]
        del kwargs["dest"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.source1)

class NOPInstruction(Instruction):
    pass

class ReturnInstruction(Instruction):
    "RETURN_VALUE_REG"
    def __init__(self, opcode, block, **kwargs):
        self.source1 = kwargs["source1"]
        del kwargs["source1"]
        super().__init__(opcode, block, **kwargs)

    @property
    def opargs(self):
        return (self.source1,)
