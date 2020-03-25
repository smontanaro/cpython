"Individual instructions."

class Instruction:
    "Represent a PyVM or RVM instruction."
    def __init__(self):
        self.length = 0
        # They come in pairs (PyVM & RVM) and reference each other
        self.sibling = None

    @property
    def sibling(self):
        "Refers to the partner instruction from the other set."
        return self._sibling

    @sibling.setter
    def sibling(self, sibling):
        assert isinstance(sibling, Instruction)
        if isinstance(self, PyVMInstruction):
            assert isinstance(sibling, RVMInstruction)
        else:
            assert isinstance(sibling, PyVMInstruction)
        self._sibling = sibling

class PyVMInstruction:
    "Specific to PyVM."

class LoadPyVMInstruction(PyVMInstruction):
    "Load from somewhere to the stack."
    def __init__(self):
        super().__init__(self)
        self.source = None

class RVMInstruction(Instruction):
    "Specific to RVM."
    def is_source(self, reg):
        raise NotImplementedError

    def is_dest(self, reg):
        raise NotImplementedError

    def is_register(self, reg):
        "Is reg a name or a register reference?"
        return reg[0:2] == "%r"

class TwoAddressRVMInstruction(RVMInstruction):
    "Two address loads."
    def __init__(self):
        super().__init__(self)
        # Load from somewhere to register.
        self.dest = None
        self.source = None

    def is_source(self, reg):
        return self.source is not None and reg == self.source

    def is_dest(self, reg):
        return self.dest is not None and reg == self.dest

    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, dest):
        # A property of defining a value for a register might be to
        # mark it as in use.
        self._dest = dest

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

class LoadFastRVMInstruction(TwoAddressRVMInstruction):
    "Load with constraint that source is another register."
    @source.setter
    def source(self, source):
        assert self.is_register(source)
        super().source(self, source)

class ThreeAddressRVMInstruction(RVMInstruction):
    "Three address binary op."
    def __init__(self):
        super().__init__(self)
        # Load from somewhere to register.
        self.dest = None
        self.source1 = None
        self.source2 = None

    def is_source(self, reg):
        return (self.source1 is not None and reg == self.source1 or
                self.source2 is not None and reg == self.source2)

    def is_dest(self, reg):
        return self.dest is not None and reg == self.dest

    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, dest):
        # A property of defining a value for a register might be to
        # mark it as in use.
        self._dest = dest

    @property
    def source1(self):
        return self._source1

    @source1.setter
    def source1(self, source1):
        self._source1 = source1

    @property
    def source2(self):
        return self._source2

    @source2.setter
    def source2(self, source2):
        self._source2 = source2
