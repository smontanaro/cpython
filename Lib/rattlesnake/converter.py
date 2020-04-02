"The actual converter class"

# TBD:
# * line number table needs to be updated

from rattlesnake import opcodes
from rattlesnake.blocks import Block
from rattlesnake.instructions import (
    Instruction, JumpIfInstruction, LoadFastInstruction, StoreFastInstruction,
    CompareOpInstruction, BinOpInstruction, NOPInstruction, LoadConstInstruction,
    LoadGlobalInstruction, JumpInstruction, ReturnInstruction,
    StoreGlobalInstruction, PyVMInstruction,
)
from rattlesnake.util import enumerate_reversed, LineNumberDict

class OptimizeFilter:
    """Base peephole optimizer class for Python byte code.

Instances of OptimizeFilter subclasses are chained together in a
pipeline, each one responsible for a single optimization."""

    NOP_OPCODE = opcodes.ISET.opmap['NOP']
    EXT_ARG_OPCODE = opcodes.ISET.opmap["EXTENDED_ARG"]

    def __init__(self, codeobj):
        """input must be a code object."""
        self.codeobj = codeobj
        self.code = codeobj.co_code
        self.varnames = codeobj.co_varnames
        self.names = codeobj.co_names
        self.constants = codeobj.co_consts
        self.blocks = {
            "PyVM": [],
            "RVM": [],
        }

    def findlabels(self, code):
        "Find target addresses in the code."
        labels = {0}
        n = len(code)
        carry_oparg = 0
        for i in range(0, n, 2):
            op, oparg = code[i:i+2]
            carry_oparg = carry_oparg << 8 | oparg
            if op == self.EXT_ARG_OPCODE:
                continue
            oparg, carry_oparg = carry_oparg, 0
            fmt = opcodes.ISET.format(op)
            if 'a' in fmt:
                # relative jump
                labels.add(i + oparg)
                #print(i, "labels:", labels)
            elif 'A' in fmt:
                # abs jump
                labels.add(oparg)
                #print(i, "labels:", labels)
        labels = sorted(labels)
        return labels

    def convert_jump_targets_to_blocks(self):
        "Convert jump target addresses to block numbers in PyVM blocks."
        blocks = self.blocks["PyVM"]
        assert blocks[0].block_type == "PyVM"
        for block in blocks:
            for instr in block:
                if instr.is_jump():
                    for tblock in blocks:
                        if instr.target_address == tblock.address:
                            instr.target = tblock.block_number
                            break
                    assert instr.target != -1
                    # No longer required.
                    del instr.target_address

    def find_blocks(self):
        """Convert code byte string to block form.

        JUMP instruction targets are converted to block numbers at the end.

        """
        blocks = self.blocks["PyVM"]
        labels = self.findlabels(self.code)
        line_numbers = LineNumberDict(self.codeobj)
        #print(">>> labels:", labels)
        n = len(self.code)
        block_num = 0
        ext_oparg = 0
        for offset in range(0, n, 2):
            if offset in labels:
                block = Block("PyVM", self, block_num)
                block.address = offset
                block_num += 1
                blocks.append(block)
            (op, oparg) = self.code[offset:offset+2]
            # Elide EXTENDED_ARG opcodes, constructing the effective
            # oparg as we go.
            if op == self.EXT_ARG_OPCODE:
                ext_oparg = ext_oparg << 8 | oparg
            else:
                oparg = ext_oparg << 8 | oparg
                instr = PyVMInstruction(op, block, opargs=(oparg,))
                if instr.is_jump():
                    address = oparg
                    if instr.is_rel_jump():
                        # Convert to absolute
                        address += offset
                    #print(f">> {block.block_number} found a JUMP"
                    #      f" @ {offset} target_addr={address}")
                    instr = JumpInstruction(op, block, address=address)
                instr.line_number = line_numbers[offset]
                block.append(instr)
                ext_oparg = 0
        self.convert_jump_targets_to_blocks()

class InstructionSetConverter(OptimizeFilter):
    """convert stack-based VM code into register-oriented VM code.

    this class consists of a series of small methods, each of which knows
    how to convert a small number of stack-based instructions to their
    register-based equivalents.  A dispatch table in optimize_block keyed
    by the stack-based instructions selects the appropriate routine.
    """

    # a subset of instructions that will suppress the conversion to the
    # register-oriented code
    bad_instructions = {opcodes.ISET.opmap['LOAD_NAME']:1,
                        opcodes.ISET.opmap['STORE_NAME']:1,
                        opcodes.ISET.opmap['DELETE_NAME']:1,
                        opcodes.ISET.opmap['SETUP_FINALLY']:1,
                        opcodes.ISET.opmap['IMPORT_FROM']:1}
    dispatch = {}

    def __init__(self, code):
        # input to this guy is a code object
        self.stacklevel = code.co_nlocals
        super().__init__(code)
        # Stack starts right after locals. Together, the locals and
        # the space allocated for the stack form a single register
        # file.
        self.max_stacklevel = self.stacklevel + code.co_stacksize
        #print(">> nlocals:", code.co_nlocals)
        #print(">> stacksize:", code.co_stacksize)
        assert self.max_stacklevel <= 127, "locals+stack are too big!"

    def set_block_stacklevel(self, target, level):
        """set the input stack level for particular block"""
        #print(">> set_block_stacklevel:", (target, level))
        self.blocks["RVM"][target].set_stacklevel(level)

    # series of operations below mimic the stack changes of various
    # stack operations so we know what slot to find particular values in
    def push(self):
        """increment and return next writable slot on the stack"""
        self.stacklevel += 1
        #print(">> push:", self.stacklevel)
        assert self.stacklevel <= self.max_stacklevel, (
            f"Overran the end of the registers!"
            f" {self.stacklevel} > {self.max_stacklevel}"
        )
        return self.stacklevel - 1

    def pop(self):
        """return top readable slot on the stack and decrement"""
        self.stacklevel -= 1
        #print(">> pop:", self.stacklevel)
        assert self.stacklevel >= self.codeobj.co_nlocals, (
            f"Stack slammed into locals!"
            f" {self.stacklevel} < {self.codeobj.co_nlocals}"
        )
        return self.stacklevel

    def top(self):
        """return top readable slot on the stack"""
        #print(">> top:", self.stacklevel)
        return self.stacklevel

    def set_stacklevel(self, level):
        """set stack level explicitly - used to handle jump targets"""
        if level < self.codeobj.co_nlocals:
            raise ValueError("invalid stack level: %d" % level)
        self.stacklevel = level
        #print(">> set:", self.stacklevel)
        return self.stacklevel

    def gen_rvm(self):
        self.find_blocks()
        self.blocks["RVM"] = []
        for pyvm_block in self.blocks["PyVM"]:
            rvm_block = Block("RVM", self, block_number=pyvm_block.block_number)
            self.blocks["RVM"].append(rvm_block)
        for (rvm, pyvm) in zip(self.blocks["RVM"], self.blocks["PyVM"]):
            pyvm.gen_rvm(rvm)

    # A small, detailed example forward propagating the result of a
    # fast load and backward propagating the result of a fast
    # store. (Using abbreviated names: LFR == LOAD_FAST_REG, etc.)

    #                       Forward    Reverse     Action
    # LFR, (2, 1)           %r2 -> %r1             NOP
    # LCR, (3, 1)               |
    # BMR, (2, 3, 2)            v          ^       src2 = %r1, dst = %r0
    # SFR, (0, 2)                      %r2 -> %r0  NOP

    # Apply actions:

    # NOP
    # LCR, (3, 1)
    # BMR, (0, 3, 1)
    # NOP

    # Delete NOPs:

    # LCR, (3, 1)
    # BMR, (0, 3, 1)

    # Result:

    # * 10 bytes in code string instead of 18

    # * Two operations, three EXT_ARG instead of four operations, five
    #   EXT_ARG

    # * One load instead of two

    # * No explicit stores

    # Consider forward propagation operating on a few
    # instructions. Before:

    #  0 Instruction(LOAD_FAST_REG, (2, 0)) (4)
    #  4 Instruction(LOAD_FAST_REG, (3, 1)) (4)
    #  8 Instruction(COMPARE_OP_REG, (2, 2, 3, 4)) (8)
    # 16 Instruction(JUMP_IF_FALSE_REG, (1, 2)) (4)
    # 20 Instruction(LOAD_FAST_REG, (2, 1)) (4)
    # 24 Instruction(LOAD_CONST_REG, (3, 1)) (4)
    # 28 Instruction(BINARY_SUBTRACT_REG, (2, 2, 3)) (6)

    # Immediately after:

    #  0 Instruction(NOP, (0,)) (2)
    #  2 Instruction(NOP, (0,)) (2)
    #  4 Instruction(COMPARE_OP_REG, (2, 0, 1, 4)) (8)
    # 12 Instruction(JUMP_IF_FALSE_REG, (1, 2)) (4)
    # 16 Instruction(NOP, (0,)) (2)
    # 18 Instruction(LOAD_CONST_REG, (3, 1)) (4)
    # 22 Instruction(BINARY_SUBTRACT_REG, (2, 1, 1)) (6)

    # When the first two LFR instructions were added to the block, we
    # push()'d, indicating that registers 2 and 3 were occupied.  When
    # forward propagation replaces them with NOPs, I think we need to
    # at least note that they are now free. pop() might not be the
    # right thing to do, as we have already added a LCR instruction
    # whose destination was register 3.  Maybe we maintain a register
    # free list?  Or maybe it doesn't matter.  We just don't use as
    # many registers.  Perhaps when someone implements a better
    # register allocation scheme the registers which were freed up in
    # this stage will be useful.

    def forward_propagate_fast_loads(self):
        "LOAD_FAST_REG should be a NOP..."
        prop_dict = {}
        dirty = None
        for block in self.blocks["RVM"]:
            for (i, instr) in enumerate(block):
                if (isinstance(instr, LoadFastInstruction) and
                    instr.name == "LOAD_FAST_REG"):
                    # Will map future references to the load's
                    # destination register to its source.
                    prop_dict[instr.dest] = instr.source1
                    # The load is no longer needed, so replace it with
                    # a NOP.
                    block[i] = NOPInstruction(self.NOP_OPCODE, block)
                    if dirty is None:
                        dirty = block.block_number
                else:
                    for srckey in ("source1", "source2"):
                        src = getattr(instr, srckey, None)
                        if src is not None:
                            setattr(instr, srckey, prop_dict.get(src, src))
                    dst = getattr(instr, "dest", None)
                    if dst is not None:
                        # If the destination register is overwritten,
                        # remove it from the dictionary as it's no
                        # longer valid.
                        try:
                            del prop_dict[dst]
                        except KeyError:
                            pass
        self.mark_dirty(dirty)

    def backward_propagate_fast_stores(self):
        "STORE_FAST_REG should be a NOP..."
        # This is similar to forward_propagate_fast_loads, but we work
        # from back to front through the block list, map src to dst in
        # STORE instructions and update source registers until we see
        # a register appear as a source in an earlier instruction.
        prop_dict = {}
        dirty = None
        for block in self.blocks["RVM"]:
            for (i, instr) in enumerate_reversed(block):
                if isinstance(instr, StoreFastInstruction):
                    # Will map earlier references to the store's
                    # source registers to its destination.
                    prop_dict[instr.source1] = instr.dest
                    # Elide...
                    block[i] = NOPInstruction(self.NOP_OPCODE, block)
                    if dirty is None:
                        dirty = block.block_number
                    else:
                        dirty = min(block.block_number, dirty)
                else:
                    dst = getattr(instr, "dest", None)
                    if dst is not None:
                        # If the destination register can be mapped to
                        # a source, replace it here.
                        instr.dest = prop_dict.get(dst, dst)
                    for srckey in ("source1", "source2"):
                        src = getattr(instr, srckey, None)
                        try:
                            del prop_dict[src]
                        except KeyError:
                            pass
        self.mark_dirty(dirty)

    def delete_nops(self):
        "NOP instructions can safely be removed."
        dirty = None
        for block in self.blocks["RVM"]:
            for (i, instr) in enumerate_reversed(block):
                if isinstance(instr, NOPInstruction):
                    del block[i]
                    if dirty is None:
                        dirty = block.block_number
                    else:
                        dirty = min(block.block_number, dirty)
        self.mark_dirty(dirty)

    def mark_dirty(self, dirty):
        "Reset addresses on dirty blocks."
        # Every block downstream from the first modified block is
        # dirty.
        if dirty is None:
            return
        for block in self.blocks["RVM"][dirty:]:
            #print("??? mark block", block.block_number, "dirty")
            block.address = -1
        # Except the address of the first block is always known.
        # pylint: disable=protected-access
        self.blocks["RVM"][0]._address = 0

    def display_blocks(self, blocks):
        "debug"
        print("globals:", self.names)
        print("locals:", self.varnames)
        print("constants:", self.constants)
        print("code len:", sum(block.codelen() for block in blocks))
        print("first lineno:", self.codeobj.co_firstlineno)
        for block in blocks:
            print(block)
            block.display()
        print()

    # def unary_convert(self, instr, block):
    #     opname = "%s_REG" % opcodes.ISET.opname[instr.opcode]
    #     src = self.pop()
    #     dst = self.push()
    #     return Instruction(opcodes.ISET.opmap[opname], block,
    #                        dest=dst, source1=src)
    # dispatch[opcodes.ISET.opmap['UNARY_INVERT']] = unary_convert
    # dispatch[opcodes.ISET.opmap['UNARY_POSITIVE']] = unary_convert
    # dispatch[opcodes.ISET.opmap['UNARY_NEGATIVE']] = unary_convert
    # dispatch[opcodes.ISET.opmap['UNARY_NOT']] = unary_convert

    def binary_convert(self, instr, block):
        opname = "%s_REG" % opcodes.ISET.opname[instr.opcode]
        ## TBD... Still not certain I have argument order/byte packing correct.
        # dst <- src1 OP src2
        src2 = self.pop()       # right-hand register src
        src1 = self.pop()       # left-hand register src
        dst = self.push()       # dst
        return BinOpInstruction(opcodes.ISET.opmap[opname], block,
                                dest=dst, source1=src1, source2=src2)
    dispatch[opcodes.ISET.opmap['BINARY_POWER']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_MULTIPLY']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_MATRIX_MULTIPLY']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_TRUE_DIVIDE']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_FLOOR_DIVIDE']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_MODULO']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_ADD']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_SUBTRACT']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_LSHIFT']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_RSHIFT']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_AND']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_XOR']] = binary_convert
    dispatch[opcodes.ISET.opmap['BINARY_OR']] = binary_convert

    # def subscript_convert(self, instr, block):
    #     op = instr.opcode
    #     if op == opcodes.ISET.opmap['BINARY_SUBSCR']:
    #         index = self.pop()
    #         obj = self.pop()
    #         dst = self.push()
    #         return Instruction(opcodes.ISET.opmap['BINARY_SUBSCR_REG'],
    #                            (obj, index, dst))
    #     if op == opcodes.ISET.opmap['STORE_SUBSCR']:
    #         index = self.pop()
    #         obj = self.pop()
    #         val = self.pop()
    #         return Instruction(opcodes.ISET.opmap['STORE_SUBSCR_REG'],
    #                            (obj, index, val))
    #     if op == opcodes.ISET.opmap['DELETE_SUBSCR']:
    #         index = self.pop()
    #         obj = self.pop()
    #         return Instruction(opcodes.ISET.opmap['DELETE_SUBSCR_REG'],
    #                            (obj, index))
    #     raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    # dispatch[opcodes.ISET.opmap['BINARY_SUBSCR']] = subscript_convert
    # dispatch[opcodes.ISET.opmap['STORE_SUBSCR']] = subscript_convert
    # dispatch[opcodes.ISET.opmap['DELETE_SUBSCR']] = subscript_convert

    # def function_convert(self, instr, block):
    #     op = instr.opcode
    #     oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    #     if op == opcodes.ISET.opmap['CALL_FUNCTION']:
    #         na = oparg[0]
    #         nk = oparg[1]
    #         src = self.top()
    #         for _ in range(na):
    #             src = self.pop()
    #         for _ in range(nk*2):
    #             src = self.pop()
    #         return Instruction(opcodes.ISET.opmap['CALL_FUNCTION_REG'],
    #                            (na, nk, src))
    #     if op == opcodes.ISET.opmap['MAKE_FUNCTION']:
    #         code = self.pop()
    #         n = oparg[0]|(oparg[1]<<8)
    #         dst = self.push()
    #         return Instruction(opcodes.ISET.opmap['MAKE_FUNCTION_REG'],
    #                            (code, n, dst))
    #     raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    # dispatch[opcodes.ISET.opmap['MAKE_FUNCTION']] = function_convert
    # dispatch[opcodes.ISET.opmap['CALL_FUNCTION']] = function_convert
    # # dispatch[opcodes.ISET.opmap['BUILD_CLASS']] = function_convert

    def jump_convert(self, instr, block):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['RETURN_VALUE']:
            opname = f"{opcodes.ISET.opname[op]}_REG"
            return ReturnInstruction(opcodes.ISET.opmap[opname], block,
                                     source1=self.pop())
        if op in (opcodes.ISET.opmap['POP_JUMP_IF_FALSE'],
                    opcodes.ISET.opmap['POP_JUMP_IF_TRUE']):
            opname = f"{opcodes.ISET.opname[op]}_REG"[4:]
            self.set_block_stacklevel(oparg, self.top())
            return JumpIfInstruction(opcodes.ISET.opmap[opname], block,
                                     target=instr.target, source1=self.pop())
        # if op in (opcodes.ISET.opmap['JUMP_FORWARD'],
        #             opcodes.ISET.opmap['JUMP_ABSOLUTE']):
        #     opname = f"{opcodes.ISET.opname[op]}_REG"
        #     self.set_block_stacklevel(oparg, self.top())
        #     return Instruction(opcodes.ISET.opmap[opname], block, (oparg,))
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['JUMP_FORWARD']] = jump_convert
    dispatch[opcodes.ISET.opmap['JUMP_ABSOLUTE']] = jump_convert
    dispatch[opcodes.ISET.opmap['POP_JUMP_IF_FALSE']] = jump_convert
    dispatch[opcodes.ISET.opmap['POP_JUMP_IF_TRUE']] = jump_convert
    dispatch[opcodes.ISET.opmap['JUMP_ABSOLUTE']] = jump_convert
    # dispatch[opcodes.ISET.opmap['FOR_LOOP']] = jump_convert
    # dispatch[opcodes.ISET.opmap['SETUP_LOOP']] = jump_convert
    dispatch[opcodes.ISET.opmap['RETURN_VALUE']] = jump_convert
    # dispatch[opcodes.ISET.opmap['BREAK_LOOP']] = jump_convert

    def load_convert(self, instr, block):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['LOAD_FAST']:
            load_class = LoadFastInstruction
        elif op == opcodes.ISET.opmap['LOAD_CONST']:
            load_class = LoadConstInstruction
        elif op == opcodes.ISET.opmap['LOAD_GLOBAL']:
            load_class = LoadGlobalInstruction
        else:
            raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")

        src = oparg         # offset into localsplus
        dst = self.push()
        opname = f"{opcodes.ISET.opname[op]}_REG"
        return load_class(opcodes.ISET.opmap[opname], block,
                          dest=dst, source1=src)
    dispatch[opcodes.ISET.opmap['LOAD_CONST']] = load_convert
    dispatch[opcodes.ISET.opmap['LOAD_GLOBAL']] = load_convert
    dispatch[opcodes.ISET.opmap['LOAD_FAST']] = load_convert

    def store_convert(self, instr, block):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['STORE_FAST']:
            store_class = StoreFastInstruction
        elif op == opcodes.ISET.opmap['STORE_GLOBAL']:
            store_class = StoreGlobalInstruction
        else:
            raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
        dst = oparg
        src = self.pop()
        opname = f"{opcodes.ISET.opname[op]}_REG"
        # Really the same thing as a LOAD_FAST_REG
        return store_class(opcodes.ISET.opmap[opname], block,
                           dest=dst, source1=src)
    dispatch[opcodes.ISET.opmap['STORE_FAST']] = store_convert
    dispatch[opcodes.ISET.opmap['STORE_GLOBAL']] = store_convert

    # def attr_convert(self, instr, block):
    #     op = instr.opcode
    #     oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    #     if op == opcodes.ISET.opmap['LOAD_ATTR']:
    #         obj = self.pop()
    #         attr = oparg
    #         dst = self.push()
    #         return Instruction(opcodes.ISET.opmap['LOAD_ATTR_REG'], block,
    #                            (dst, obj, attr))
    #     if op == opcodes.ISET.opmap['STORE_ATTR']:
    #         obj = self.pop()
    #         attr = oparg
    #         val = self.pop()
    #         return Instruction(opcodes.ISET.opmap['STORE_ATTR_REG'], block,
    #                            (obj, attr, val))
    #     if op == opcodes.ISET.opmap['DELETE_ATTR']:
    #         obj = self.pop()
    #         attr = oparg
    #         return Instruction(opcodes.ISET.opmap['DELETE_ATTR_REG'], block,
    #                            (obj, attr))
    #     raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    # dispatch[opcodes.ISET.opmap['STORE_ATTR']] = attr_convert
    # dispatch[opcodes.ISET.opmap['DELETE_ATTR']] = attr_convert
    # dispatch[opcodes.ISET.opmap['LOAD_ATTR']] = attr_convert

    # def seq_convert(self, instr, block):
    #     op = instr.opcode
    #     oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    #     if op == opcodes.ISET.opmap['BUILD_MAP']:
    #         dst = self.push()
    #         return Instruction(opcodes.ISET.opmap['BUILD_MAP_REG'], block,
    #                            (dst,))
    #     opname = "%s_REG" % opcodes.ISET.opname[op]
    #     if op in (opcodes.ISET.opmap['BUILD_LIST'],
    #                  opcodes.ISET.opmap['BUILD_TUPLE']):
    #         n = oparg
    #         for _ in range(n):
    #             self.pop()
    #         src = self.top()
    #         dst = self.push()
    #         return Instruction(opcodes.ISET.opmap[opname], block,
    #                            (dst, n, src))
    #     if op == opcodes.ISET.opmap['UNPACK_SEQUENCE']:
    #         n = oparg
    #         src = self.pop()
    #         for _ in range(n):
    #             self.push()
    #         return Instruction(opcodes.ISET.opmap[opname], block,
    #                            (n, src))
    #     raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    # dispatch[opcodes.ISET.opmap['BUILD_TUPLE']] = seq_convert
    # dispatch[opcodes.ISET.opmap['BUILD_LIST']] = seq_convert
    # dispatch[opcodes.ISET.opmap['BUILD_MAP']] = seq_convert
    # dispatch[opcodes.ISET.opmap['UNPACK_SEQUENCE']] = seq_convert

    def compare_convert(self, instr, block):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['COMPARE_OP']:
            cmpop = oparg
            src2 = self.pop()
            src1 = self.pop()
            dst = self.push()
            return CompareOpInstruction(opcodes.ISET.opmap['COMPARE_OP_REG'],
                                        block,
                                        dest=dst, source1=src1,
                                        source2=src2, compare_op=cmpop)
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['COMPARE_OP']] = compare_convert

    # def stack_convert(self, instr, block):
    #     op = instr.opcode
    #     if op == opcodes.ISET.opmap['POP_TOP']:
    #         self.pop()
    #         return NOPInstruction(self.NOP_OPCODE, block)
    #     if op == opcodes.ISET.opmap['DUP_TOP']:
    #         # nop
    #         _dummy = self.top()
    #         _dummy = self.push()
    #         return NOPInstruction(self.NOP_OPCODE, block)
    #     if op == opcodes.ISET.opmap['ROT_TWO']:
    #         return Instruction(opcodes.ISET.opmap['ROT_TWO_REG'], block,
    #                            (self.top(),))
    #     if op == opcodes.ISET.opmap['ROT_THREE']:
    #         return Instruction(opcodes.ISET.opmap['ROT_THREE_REG'], block,
    #                            (self.top(),))
    #     if op == opcodes.ISET.opmap['POP_BLOCK']:
    #         return Instruction(opcodes.ISET.opmap['POP_BLOCK_REG'], block)
    #     raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    # dispatch[opcodes.ISET.opmap['POP_TOP']] = stack_convert
    # dispatch[opcodes.ISET.opmap['ROT_TWO']] = stack_convert
    # dispatch[opcodes.ISET.opmap['ROT_THREE']] = stack_convert
    # dispatch[opcodes.ISET.opmap['DUP_TOP']] = stack_convert
    # dispatch[opcodes.ISET.opmap['POP_BLOCK']] = stack_convert

    def misc_convert(self, instr, block):
        op = instr.opcode
        # if op == opcodes.ISET.opmap['IMPORT_NAME']:
        #     dst = self.push()
        #     return Instruction(opcodes.ISET.opmap['IMPORT_NAME_REG'], block,
        #                        (dst, oparg[0]))
        # opname = "%s_REG" % opcodes.ISET.opname[op]
        # if op == opcodes.ISET.opmap['PRINT_EXPR']:
        #     src = self.pop()
        #     return Instruction(opcodes.ISET.opmap[opname], block, (src,))
        if op == opcodes.ISET.opmap['EXTENDED_ARG']:
            return Instruction(op, block)
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['IMPORT_NAME']] = misc_convert
    dispatch[opcodes.ISET.opmap['PRINT_EXPR']] = misc_convert
    dispatch[opcodes.ISET.opmap['EXTENDED_ARG']] = misc_convert

    def __bytes__(self):
        "Return generated byte string."
        instr_bytes = []
        for block in self.blocks["RVM"]:
            instr_bytes.append(bytes(block))
        return b"".join(instr_bytes)

    def get_lnotab(self):
        firstlineno = self.codeobj.co_firstlineno
        last_line_number = firstlineno
        last_address = 0
        address = 0
        lnotab = []
        for block in self.blocks["RVM"]:
            for instr in block.instructions:
                line_number = instr.line_number
                print(f"lno: {address} -> {line_number} ({last_line_number})")
                if line_number > last_line_number:
                    offset = line_number - last_line_number
                    print(f"lno offset: {offset}")
                    lnotab.append(address - last_address)
                    lnotab.append(offset)
                    last_line_number = line_number
                    last_address = address
                address += len(instr)
        return bytes(lnotab)
