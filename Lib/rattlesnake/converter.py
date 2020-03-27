"The actual converter class"

import copy

from rattlesnake import opcodes
from rattlesnake.blocks import Block
from rattlesnake.instructions import (
    Instruction, JumpIfInstruction, LoadFastInstruction, StoreFastInstruction,
    CompareOpInstruction, BinOpInstruction, NOPInstruction,
    LoadGlobalInstruction,
)
from rattlesnake.util import enumerate_reversed

class OptimizeFilter:
    """Base peephole optimizer class for Python byte code.

Instances of OptimizeFilter subclasses are chained together in a
pipeline, each one responsible for a single optimization."""

    NOP_INST = NOPInstruction(opcodes.ISET.opmap['NOP'])
    EXT_ARG_OPCODE = opcodes.ISET.opmap["EXTENDED_ARG"]

    def __init__(self, codeobj):
        """input can be a list as emitted by code_to_blocks or another
OptimizeFilter instance. varnames and constants args are just placeholders
for the future."""
        self.codeobj = codeobj
        self.code = codeobj.co_code
        self.varnames = codeobj.co_varnames
        self.names = codeobj.co_names
        self.constants = codeobj.co_consts
        self.address_to_block = {}
        self.blocks = []
        self.output = []

    def findlabels(self, code):
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

    def reset(self):
        self.output = None
        try:
            self.blocks.reset()
        except AttributeError:
            # will happen if the input is a list
            pass

    def compute_block_addresses(self, blocks):
        "Populate address_to_block dict for a list of blocks (PyVM or RVM)."
        instr_address = 0
        for (bi, block) in enumerate(blocks):
            #print("addr:", instr_address, "bi:", bi)
            block.address = instr_address
            self.address_to_block[instr_address] = bi
            instr_address += block.codelen()
        #print("a2b:", self.address_to_block)

    def convert_address_to_block(self):
        "Replace jump targets with block numbers in PyVM blocks."
        # Note that we should probably zero out EXTENDED_ARG oparg
        # values but retain them for display. None of my meager
        # examples so far contain them, so I will sidestep that issue
        # for the moment.
        instr_address = 0
        for block in self.blocks:
            for (i, instr) in enumerate(block):
                if not instr.is_jump():
                    continue
                oparg = self.compute_full_oparg(block, i)
                if instr.is_rel_jump():
                    # oparg is relative to the start of the current
                    # instruction address.
                    oparg += instr_address
                try:
                    instr.opargs = (self.address_to_block[oparg],)
                except KeyError:
                    print(self.address_to_block)
                    raise
                instr_address += len(instr)

    def compute_full_oparg(self, block, i, zero=True):
        "Construct a full oparg value taking EXTENDED_ARG into account."
        # zero=TRUE means EXT_ARG opargs should be replaced with (0,).

        # All PyVM instructions are two bytes long. This code assumes
        # that. I believe it should work with RVM as long as we are
        # only dealing with jumps, which is its original intended use.

        # Work backwards, looking for the first instruction which
        # isn't EXT_ARG.
        j = i - 1
        while j >= 0:
            if block[j].opcode != self.EXT_ARG_OPCODE:
                # Back to the first EXT_ARG or the actual instruction
                # of interest.
                j += 1
                break
            j -= 1
        # Now perform the usual oparg calculation.
        oparg = 0
        while j < i:
            oparg = oparg << 8 | block[j].opargs[0]
            if zero:
                block[j].opargs = (0,)
            j += 1
        oparg = oparg << 8 | block[i].opargs[0]
        return oparg

    def find_blocks(self):
        """Convert code byte string to block form."""
        blocks = self.blocks
        labels = self.findlabels(self.code)
        #print(">>> labels:", labels)
        n = len(self.code)
        block_num = 0
        for i in range(0, n, 2):
            if i in labels:
                #print(f">> new block number={len(blocks)} offset={i}")
                new_block = Block("PyVM")
                new_block.block_number = block_num
                new_block.address = i
                block_num += 1
                blocks.append(new_block)
            (op, oparg) = self.code[i:i+2]
            blocks[-1].append(Instruction(op, (oparg,)))
        self.compute_block_addresses(blocks)

    def constant_value(self, op):
        if op[0] == opcodes.ISET.opmap["LOAD_CONST"]:
            return self.constants[op[1][0]+(op[1][1]<<8)]
        if op[0] == opcodes.ISET.opmap["LOADI"]:
            return op[1][0]+(op[1][1]<<8)
        raise ValueError("Not a load constant opcode: %d"%op[0])

    def find_constant(self, c):
        # return the index of c in self.constants, adding it if it's not there
        try:
            index = self.constants.index(c)
        except ValueError:
            self.constants.append(c)
            index = self.constants.index(c)
        return index

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
        self.rvm_blocks = []

    def set_block_stacklevel(self, target, level):
        """set the input stack level for particular block"""
        #print(">> set:", (target, level))
        try:
            self.blocks[target].set_stacklevel(level)
        except IndexError:
            print("!!", target, level, len(self.blocks))
            raise

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
        self.rvm_blocks = []
        pyvm_offset = rvm_offset = 0
        for (i, block) in enumerate(self.blocks):
            rvm_block = block.gen_rvm(self)
            self.rvm_blocks.append(rvm_block)

            # address/block number calculation
            block.block_number = i
            rvm_block.address = rvm_offset
            rvm_block.block_number = i

            pyvm_offset += block.codelen()
            # TBD: PyVM code does not change, but RVM code changes as
            # we optimize, so this offset will change. Still, useful
            # to have it for display purposes.
            rvm_offset += rvm_block.codelen()

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

    def forward_propagate_fast_reads(self):
        "LOAD_FAST_REG should be a NOP..."
        prop_dict = {}
        for block in self.rvm_blocks:
            for (i, instr) in enumerate(block):
                if isinstance(instr, LoadFastInstruction):
                    # Will map future references to the load's
                    # destination register to its source.
                    src = instr.source_registers()[0]
                    dst = instr.dest_registers()[0]
                    prop_dict[dst] = src
                    # The load is no longer needed, so replace it with
                    # NOP.
                    block[i] = self.NOP_INST
                else:
                    sources = instr.source_registers()
                    dests = instr.dest_registers()
                    if not sources and not dests:
                        continue
                    if set(sources) & set(prop_dict):
                        # Map any register references saved in our
                        # propagation dictionary to the saved
                        # source register(s).
                        new_sources = []
                        for src in sources:
                            new_sources.append(prop_dict.get(src, src))
                        new_sources = tuple(new_sources)
                        if new_sources != sources:
                            instr.update_opargs(source=new_sources)
                    for dst in dests:
                        # If the destination register is overwritten,
                        # remove it from the dictionary as it's no
                        # longer valid.
                        try:
                            del prop_dict[dst]
                        except KeyError:
                            pass

    def backward_propagate_fast_writes(self):
        "STORE_FAST_REG should be a NOP..."
        # This is similar to forward_propagate, but we work from back
        # to front through the block list, map src to dst in STORE
        # instructions, and update source registers until we see a
        # register appear as a source.
        prop_dict = {}
        for block in self.rvm_blocks:
            for (i, instr) in enumerate_reversed(block):
                if isinstance(instr, StoreFastInstruction):
                    # Will map earlier references to the store's
                    # source registers to its destination.
                    src = instr.source_registers()[0]
                    dst = instr.dest_registers()[0]
                    prop_dict[src] = dst
                    # Elide...
                    block[i] = self.NOP_INST
                else:
                    sources = instr.source_registers()
                    dests = instr.dest_registers()
                    if dests:
                        # If the destination register can be mapped to
                        # a source, replace it here.
                        dst = instr.dest_registers()[0]
                        new_dst = prop_dict.get(dst, dst)
                        if dst != new_dst:
                            instr.update_opargs(dest=(new_dst,))
                    for src in sources:
                        # Register reads kill a mapping.
                        try:
                            del prop_dict[src]
                        except KeyError:
                            pass

    def delete_nops(self):
        "NOP instructions can safely be removed."
        for block in self.rvm_blocks:
            for (i, instr) in enumerate_reversed(block):
                if isinstance(instr, NOPInstruction):
                    del block[i]

    def display_blocks(self, blocks):
        "debug"
        print("globals:", self.names)
        print("locals:", self.varnames)
        print("constants:", self.constants)
        print("code len:", sum(block.codelen() for block in blocks))
        for block in blocks:
            block.display()
        print()

    def unary_convert(self, instr):
        opname = "%s_REG" % opcodes.ISET.opname[instr.opcode]
        src = self.pop()
        dst = self.push()
        return Instruction(opcodes.ISET.opmap[opname], (dst, src))
    dispatch[opcodes.ISET.opmap['UNARY_INVERT']] = unary_convert
    dispatch[opcodes.ISET.opmap['UNARY_POSITIVE']] = unary_convert
    dispatch[opcodes.ISET.opmap['UNARY_NEGATIVE']] = unary_convert
    dispatch[opcodes.ISET.opmap['UNARY_NOT']] = unary_convert

    def binary_convert(self, instr):
        opname = "%s_REG" % opcodes.ISET.opname[instr.opcode]
        ## TBD... Still not certain I have argument order/byte packing correct.
        # dst <- src1 OP src2
        src1 = self.pop()       # left-hand register src
        src2 = self.pop()       # right-hand register src
        dst = self.push()       # dst
        return BinOpInstruction(opcodes.ISET.opmap[opname], (dst, src1, src2))
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

    # Not quite yet...
    # def inplace_convert(self, instr):
    #     opname = "%s_REG" % opcodes.ISET.opname[instr.opcode]
    #     ## TBD... Still not certain I have argument order/byte packing correct.
    #     # dst <- src1 OP src2
    #     src1 = self.pop()       # left-hand register src
    #     src2 = self.pop()       # right-hand register src
    #     dst = self.push()       # dst
    #     return Instruction(opcodes.ISET.opmap[opname], (dst, src1, src2))
    # dispatch[opcodes.ISET.opmap['INPLACE_POWER']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_MULTIPLY']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_MATRIX_MULTIPLY']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_TRUE_DIVIDE']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_FLOOR_DIVIDE']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_MODULO']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_ADD']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_SUBTRACT']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_LSHIFT']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_RSHIFT']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_AND']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_XOR']] = inplace_convert
    # dispatch[opcodes.ISET.opmap['INPLACE_OR']] = inplace_convert

    def subscript_convert(self, instr):
        op = instr.opcode
        if op == opcodes.ISET.opmap['BINARY_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            dst = self.push()
            return Instruction(opcodes.ISET.opmap['BINARY_SUBSCR_REG'],
                               (obj, index, dst))
        if op == opcodes.ISET.opmap['STORE_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            val = self.pop()
            return Instruction(opcodes.ISET.opmap['STORE_SUBSCR_REG'],
                               (obj, index, val))
        if op == opcodes.ISET.opmap['DELETE_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            return Instruction(opcodes.ISET.opmap['DELETE_SUBSCR_REG'],
                               (obj, index))
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['BINARY_SUBSCR']] = subscript_convert
    dispatch[opcodes.ISET.opmap['STORE_SUBSCR']] = subscript_convert
    dispatch[opcodes.ISET.opmap['DELETE_SUBSCR']] = subscript_convert

    def function_convert(self, instr):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['CALL_FUNCTION']:
            na = oparg[0]
            nk = oparg[1]
            src = self.top()
            for _ in range(na):
                src = self.pop()
            for _ in range(nk*2):
                src = self.pop()
            return Instruction(opcodes.ISET.opmap['CALL_FUNCTION_REG'],
                               (na, nk, src))
        if op == opcodes.ISET.opmap['MAKE_FUNCTION']:
            code = self.pop()
            n = oparg[0]|(oparg[1]<<8)
            dst = self.push()
            return Instruction(opcodes.ISET.opmap['MAKE_FUNCTION_REG'],
                               (code, n, dst))
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['MAKE_FUNCTION']] = function_convert
    dispatch[opcodes.ISET.opmap['CALL_FUNCTION']] = function_convert
    # dispatch[opcodes.ISET.opmap['BUILD_CLASS']] = function_convert

    def jump_convert(self, instr):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['RETURN_VALUE']:
            opname = f"{opcodes.ISET.opname[op]}_REG"
            val = self.pop()
            return Instruction(opcodes.ISET.opmap[opname], (val,))
        if op in (opcodes.ISET.opmap['POP_JUMP_IF_FALSE'],
                    opcodes.ISET.opmap['POP_JUMP_IF_TRUE']):
            opname = f"{opcodes.ISET.opname[op]}_REG"[4:]
            self.set_block_stacklevel(oparg, self.top())
            return JumpIfInstruction(opcodes.ISET.opmap[opname],
                                     (oparg, self.pop()))
        if op in (opcodes.ISET.opmap['JUMP_FORWARD'],
                    opcodes.ISET.opmap['JUMP_ABSOLUTE']):
            opname = f"{opcodes.ISET.opname[op]}_REG"
            self.set_block_stacklevel(oparg, self.top())
            return Instruction(opcodes.ISET.opmap[opname], (oparg,))
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

    def load_convert(self, instr):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['LOAD_FAST']:
            src = oparg         # offset into localsplus
            dst = self.push()   # unused
            return LoadFastInstruction(opcodes.ISET.opmap['LOAD_FAST_REG'],
                                       (dst, src))
        if op == opcodes.ISET.opmap['LOAD_CONST']:
            src = oparg         # reference into co_consts
            dst = self.push()   # offset into localsplus
            return Instruction(opcodes.ISET.opmap['LOAD_CONST_REG'],
                               (dst, src))
        if op == opcodes.ISET.opmap['LOAD_GLOBAL']:
            src = oparg         # global name to be found
            dst = self.push()   # offset into localsplus
            return LoadGlobalInstruction(opcodes.ISET.opmap['LOAD_GLOBAL_REG'],
                                         (dst, src))
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['LOAD_CONST']] = load_convert
    dispatch[opcodes.ISET.opmap['LOAD_GLOBAL']] = load_convert
    dispatch[opcodes.ISET.opmap['LOAD_FAST']] = load_convert

    def store_convert(self, instr):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['STORE_FAST']:
            dst = oparg
            src = self.pop()
            # Really the same thing as a LOAD_FAST_REG
            return StoreFastInstruction(opcodes.ISET.opmap['STORE_FAST_REG'],
                                        (dst, src))
        if op == opcodes.ISET.opmap['STORE_GLOBAL']:
            dst = oparg
            src = self.pop()
            return Instruction(opcodes.ISET.opmap['STORE_GLOBAL_REG'],
                               (dst, src))
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['STORE_FAST']] = store_convert
    dispatch[opcodes.ISET.opmap['STORE_GLOBAL']] = store_convert

    def attr_convert(self, instr):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['LOAD_ATTR']:
            obj = self.pop()
            attr = oparg
            dst = self.push()
            return Instruction(opcodes.ISET.opmap['LOAD_ATTR_REG'],
                               (dst, obj, attr))
        if op == opcodes.ISET.opmap['STORE_ATTR']:
            obj = self.pop()
            attr = oparg
            val = self.pop()
            return Instruction(opcodes.ISET.opmap['STORE_ATTR_REG'],
                               (obj, attr, val))
        if op == opcodes.ISET.opmap['DELETE_ATTR']:
            obj = self.pop()
            attr = oparg
            return Instruction(opcodes.ISET.opmap['DELETE_ATTR_REG'],
                               (obj, attr))
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['STORE_ATTR']] = attr_convert
    dispatch[opcodes.ISET.opmap['DELETE_ATTR']] = attr_convert
    dispatch[opcodes.ISET.opmap['LOAD_ATTR']] = attr_convert

    def seq_convert(self, instr):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['BUILD_MAP']:
            dst = self.push()
            return Instruction(opcodes.ISET.opmap['BUILD_MAP_REG'], (dst,))
        opname = "%s_REG" % opcodes.ISET.opname[op]
        if op in (opcodes.ISET.opmap['BUILD_LIST'],
                     opcodes.ISET.opmap['BUILD_TUPLE']):
            n = oparg
            for _ in range(n):
                self.pop()
            src = self.top()
            dst = self.push()
            return Instruction(opcodes.ISET.opmap[opname], (dst, n, src))
        if op == opcodes.ISET.opmap['UNPACK_SEQUENCE']:
            n = oparg
            src = self.pop()
            for _ in range(n):
                self.push()
            return Instruction(opcodes.ISET.opmap[opname], (n, src))
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['BUILD_TUPLE']] = seq_convert
    dispatch[opcodes.ISET.opmap['BUILD_LIST']] = seq_convert
    dispatch[opcodes.ISET.opmap['BUILD_MAP']] = seq_convert
    dispatch[opcodes.ISET.opmap['UNPACK_SEQUENCE']] = seq_convert

    def compare_convert(self, instr):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['COMPARE_OP']:
            cmpop = oparg
            src2 = self.pop()
            src1 = self.pop()
            dst = self.push()
            return CompareOpInstruction(opcodes.ISET.opmap['COMPARE_OP_REG'],
                                        (dst, src1, src2, cmpop))
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['COMPARE_OP']] = compare_convert

    def stack_convert(self, instr):
        op = instr.opcode
        if op == opcodes.ISET.opmap['POP_TOP']:
            self.pop()
            return self.NOP_INST
        if op == opcodes.ISET.opmap['DUP_TOP']:
            # nop
            _dummy = self.top()
            _dummy = self.push()
            return self.NOP_INST
        if op == opcodes.ISET.opmap['ROT_TWO']:
            return Instruction(opcodes.ISET.opmap['ROT_TWO_REG'],
                               (self.top(),))
        if op == opcodes.ISET.opmap['ROT_THREE']:
            return Instruction(opcodes.ISET.opmap['ROT_THREE_REG'],
                               (self.top(),))
        if op == opcodes.ISET.opmap['POP_BLOCK']:
            return Instruction(opcodes.ISET.opmap['POP_BLOCK_REG'])
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['POP_TOP']] = stack_convert
    dispatch[opcodes.ISET.opmap['ROT_TWO']] = stack_convert
    dispatch[opcodes.ISET.opmap['ROT_THREE']] = stack_convert
    dispatch[opcodes.ISET.opmap['DUP_TOP']] = stack_convert
    dispatch[opcodes.ISET.opmap['POP_BLOCK']] = stack_convert

    def misc_convert(self, instr):
        op = instr.opcode
        oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['IMPORT_NAME']:
            dst = self.push()
            return Instruction(opcodes.ISET.opmap['IMPORT_NAME_REG'],
                               (dst, oparg[0]))
        opname = "%s_REG" % opcodes.ISET.opname[op]
        if op == opcodes.ISET.opmap['PRINT_EXPR']:
            src = self.pop()
            return Instruction(opcodes.ISET.opmap[opname], (src,))
        if op == opcodes.ISET.opmap['EXTENDED_ARG']:
            return copy.copy(instr)
        raise ValueError(f"Unhandled opcode {opcodes.ISET.opname[op]}")
    dispatch[opcodes.ISET.opmap['IMPORT_NAME']] = misc_convert
    dispatch[opcodes.ISET.opmap['PRINT_EXPR']] = misc_convert
    dispatch[opcodes.ISET.opmap['EXTENDED_ARG']] = misc_convert
