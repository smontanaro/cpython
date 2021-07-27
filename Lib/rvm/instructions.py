"""Individual instructions.

Each Instruction object has an opcode (a fixed integer) and both name
and opargs attributes which are implemented as properties. They
reference back to the block where they are defined (again, a fixed
attribute). In addition, various Instruction subclasses may implement
other attributes needed for specialized tasks. For example, jump
instructions need to calculate addresses (relative or absolute) which
will depend on their enclosing block's address.

"""

import atexit
import opcode
import sys

from .util import EXT_ARG_OPCODE

class Instruction:
    """Represent an instruction in either PyVM or RVM.

    Instruction opargs are currently represented by a tuple. Its
    makeup varies by Instruction subclass.

    """

    counters = {}               # count what we convert
    dump_at_end = True

    def __init__(self, op, block, **kwargs):
        self.opcode = op
        self._opargs = (0,)
        self.block = block
        # Index into parent block's instructions list.
        self.index = -1
        # unset (or same as previous instruction?)
        self.line_number = -1
        if kwargs:
            raise ValueError(f"Non-empty kwargs at top level {kwargs}")
        if "_REG" in self.name:
            counters = Instruction.counters
            counters[self.name] = counters.get(self.name, 0) + 1

    @property
    def name(self):
        "Human-readable name for the opcode."
        return opcode.opname[self.opcode]

    @property
    def opargs(self):
        """Overrideable property

        opargs will be composed of different bits for different instructions.
        """
        return self._opargs

    def _non_zero_opargs(self):
        # self.opargs[0] is part of the instruction, so doesn't count.
        # The elements of self.opargs[1:] count, ignoring leading
        # zeroes.
        opargs = self.opargs#[1:]
        while opargs and opargs[0] == 0:
            opargs = opargs[1:]
        print(f">> {self.name}.non-zero opargs:", opargs)
        return opargs

    def _n_extarg(self):
        "Compute how many EXTENDED_ARG opcodes are necessary."
        return len(self._non_zero_opargs())

    def _ext_arg_instructions(self):
        "Return list of required EXT_ARG instructions."
        opargs = self._non_zero_opargs()
        ext_arg_instrs = []
        for arg in opargs:
            inst = ExtArgInstruction(EXT_ARG_OPCODE, block=self.block,
                                     opargs=(arg,))
            inst.line_number = self.line_number
            ext_arg_instrs.append(inst)
        return ext_arg_instrs

    def __len__(self):
        "Compute instructions required to implement self."
        # In wordcode, an instruction is op, arg, each taking one
        # byte. If we have more than zero or one arg, we use
        # EXTENDED_ARG instructions to carry the other args, each
        # again two bytes.  With Python 3.10, jump offsets became
        # denominated in instructions instead of bytes, so all we
        # count are the number of instructions, not their total
        # length.
        return 1 + self._n_extarg()

    def __str__(self):
        me = self.__dict__.copy()
        del me["block"], me["opcode"]
        return f"Instruction({self.line_number}: {self.name}, {me})"

    def is_abs_jump(self):
        "True if opcode is an absolute jump."
        return self.opcode in opcode.hasjabs

    def is_rel_jump(self):
        "True if opcode is a relative jump."
        return self.opcode in opcode.hasjrel

    def is_jump(self):
        "True for any kind of jump."
        return self.is_abs_jump() or self.is_rel_jump()

    def __bytes__(self):
        "Generate wordcode."
        code = []
        for arg in self.opargs[:-1]:
            if arg is not None:
                code.append(EXT_ARG_OPCODE)
                code.append(arg)
        code.append(self.opcode)
        code.append(self.opargs[-1])
        return bytes(code)

    def populate(self, attrs, kwargs):
        "Set attr names from kwargs dict and delete those keys."
        for attr in attrs:
            try:
                setattr(self, attr, kwargs[attr])
            except KeyError:
                print(attr, kwargs, file=sys.stderr)
                raise
            del kwargs[attr]

    @staticmethod
    def dumpcounts():
        # If nothing was counted, assume test_rvm wasn't run at all.
        total = sum(Instruction.counters.values())
        if not Instruction.dump_at_end or not total:
            return
        header = False
        for nm in sorted(Instruction.counters):
            count = Instruction.counters[nm]
            if count == 0:
                if not header:
                    print("Untested _REG instructions:")
                    header = True
                print(nm, end=" ")
        if header:
            print()

class PyVMInstruction(Instruction):
    "For basic PyVM instructions."
    def __init__(self, op, block, **kwargs):
        opargs = kwargs["opargs"]
        del kwargs["opargs"]
        super().__init__(op, block, **kwargs)
        self._opargs = opargs

class ExtArgInstruction(PyVMInstruction):
    "Simple, reused from PyVM."
    pass

class NOPInstruction(Instruction):
    "nop"
    pass

for nm in opcode.opname:
    if "_REG" in nm:
        Instruction.counters[nm] = 0

atexit.register(Instruction.dumpcounts)
