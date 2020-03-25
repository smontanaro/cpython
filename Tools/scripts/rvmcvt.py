"""NOTE: This comes from the old Rattlesnake work. It's useful here
initially as documentation of how I did things way back when. The more
I struggle with the current AST-based compiler, the more I think I
will revert to this method as proof-of-concept. Let someone else make
it production-ready if it proves to be worthwhile.

In the new formulation, I plan to retain 16-bit word code, relying
on EXTENDED_ARGS to encode extra arguments where necessary.

No matter how many arguments there are, the overall instruction is
encoded as follows (my math needs to be checked here):

* Big endian: (OP << 8 | ARG1) << 16 | (ARG2 << 8 | ARG3)

* Little endian: (OP | ARG1 << 8) << 16 | (ARG2 | ARG3 << 8)

The two-arg and three-arg cases require, respectively, one or two
EXTENDED_ARG opcodes ahead of them. EXTENDED_ARG works by saving the
current oparg, setting the next opcode and oparg, shifting the old
oparg by 8 bits, then oring that with the new oparg. It then jumps
directly to the next opcode. I doubt the performance hit would be
much, since EXTENDED_ARG is so minimal, a couple bitwise operations
and a jump.

Using EXTENDED_ARG should solve the problem of trying to squeeze four
args into 32 bits for COMPARE_OP. oparg can be up to four bytes. That
really requires four arguments, the comparison operator as well as
destination and two source registers. In the quad-byte opcode
formulation I could only easily squeeze three operand arg bytes into
the instruction. With word code I can just punt and offer up three
EXTENDED_ARG instructions before COMPARE_OP.

EXTENDED_ARG dst
EXTENDED_ARG src1
EXTENDED_ARG src2
COMPARE_OP operator

The oparg constructed by the three EXTENDED_ARG opcodes and COMPARE_OP
itself would be

(((dst << 8) | src1) << 8 | src2) << 8 | operator & 0xff

or

dst << 24 | src1 << 16 | src2 << 8 | operator

It would be nice if oparg was unsigned, but I doubt it will be a
practical problem that it's not. I think you can just say that the
number of locals and stack or registers is limited to 127 in the
CPython implementation. (This suggests a simple check during
execution, asserting that co_nlocals + co_stacksize <= 127.)

"""

import sys

# TBD... will change at some point
import regopcodes as opcodes

from rattlesnake import *

__version__ = "0.0"

class Block:
    """represent a block of code with a single entry point (first instr)"""
    def __init__(self):
        self.block = []
        self.stacklevel = -1
        self.length = 0

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

    def get_stacklevel(self):
        return self.stacklevel

    def append(self, op):
        self.block.append(op)
        self.length += 2 + len(op[1][:-1])

    def extend(self, op):
        self.block.extend(op)

    def insert(self, i, item):
        self.block.insert(i, item)

    def remove(self, item):
        self.block.remove(item)

    def __setitem__(self, i, item):
        self.block[i] = item

    def __getitem__(self, i):
        return self.block[i]

    def __len__(self):
        return len(self.block)

    def __delitem__(self, i):
        del self.block[i]

    def __getslice__(self, i, j):
        return self.block[i:j]

    def __setslice__(self, i, j, lst):
        self.block[i:j] = lst

    def __delslice__(self, i, j):
        del self.block[i:j]


class OptimizeFilter:
    """Base peephole optimizer class for Python byte code.

Instances of OptimizeFilter subclasses are chained together in a
pipeline, each one responsible for a single optimization."""

    def __init__(self, code):
        """input can be a list as emitted by code_to_blocks or another
OptimizeFilter instance. varnames and constants args are just placeholders
for the future."""
        self.code = code
        self.varnames = code.co_varnames
        self.names = code.co_names
        self.constants = code.co_consts
        self.input = []
        self.output = []

    @debug_method
    def findlabels(self, code):
        labels = {0}
        n = len(code)
        i = 0
        while i < n:
            op = code[i]
            opname = opcodes.ISET.opname[op]
            fmt = opcodes.ISET.format(op)
            if len(fmt) == 1:
                # stack
                addr = code[i+1]
                i += 2
            else:
                # register
                assert len(fmt) == 3, (opname, fmt, len(fmt))
                addr = code[i+1] | code[i+2] << 8 | code[i+3] << 16
                i += 4
            #print(f"addr == {addr}")
            if 'a' in fmt:
                # relative jump
                labels.add(i + addr)
                #print(i, "labels:", labels)
            elif 'A' in fmt:
                # abs jump
                labels.add(addr)
                #print(i, "labels:", labels)
        labels = sorted(labels)
        return labels

    def optimize(self):
        """Optimize each block in the input blocks."""
        blocks = self.input
        self.output = [None]*len(blocks)
        for i, block in enumerate(blocks):
            self.output[i] = self.optimize_block(block)

    def optimize_block(self, block):
        # noop - subclasses will override this
        return block

    def reset(self):
        self.output = None
        try:
            self.input.reset()
        except AttributeError:
            # will happen if the input is a list
            pass

    @debug_method
    def find_blocks(self):
        """Convert code string to block form."""
        blocks = []
        labels = self.findlabels(self.code)
        #print(">>> labels:", labels)
        n = len(self.code)
        i = 0
        while i < n:
            if i in labels:
                print(f">> new block offset={i}")
                blocks.append(Block())
            op = self.code[i]
            opname = opcodes.ISET.opname[op]
            oparg = self.code[i+1]
            block = blocks[-1]
            fmt = opcodes.ISET.format(op)
            if opcodes.ISET.has_argument(op):
                try:
                    if 'A' in fmt:
                        idx = labels.index(oparg)
                        print(f"  {i:4d} append: {opname} {op} {idx}")
                        block.append((op, (idx,)))
                    elif 'a' in fmt:
                        idx = labels.index(i+2+oparg)
                        print(f"  {i:4d} append: {opname} {op} {idx}")
                        block.append((op, (idx,)))
                    else:
                        print(f"  {i:4d} append: {opname} {op} {oparg}")
                        block.append((op, (oparg,)))
                except ValueError:
                    print(">>", labels)
                    raise
            else:
                assert oparg == 0, (i, self.code[i:], oparg)
                print(f"  {i:4d} append: {opname} {op} {oparg}")
                block.append((op, (oparg,)))
            i += 2
        return blocks

    def generate_code(self):
        """Convert the block form of the code back to a string."""
        self._insure_output()
        blockaddrs = [0]
        for block in self.output:
            blockaddrs.append(2 * len(block) + blockaddrs[-1])

        codelist = []
        i = 1
        ext_arg = opcodes.ISET.opmap["EXTENDED_ARG"] << 8
        for block in self.output:
            for (opcode, opargs) in block:
                print("code:", opcode, opcodes.ISET.opname[opcode], opargs)
                fmt = opcodes.ISET.format(opcode)
                if not opargs:
                    opargs = (0,)
                for oparg in opargs[0:-1]:
                    codelist.append(ext_arg | oparg)
                codelist.append(opcode << 8 | opargs[-1])
                #print(">>", (i, opcodes.ISET.opname[inst[0]], fmt), end=" ")
                i += 1
                if 'A' in fmt:
                    arg = opargs[0]
                    i += 1
                    #print("block:", arg[0]|(arg[1]<<8), end=" ")
                    addr = blockaddrs[arg]
                    #print("address:", addr, end=" ")
                    #print("encoded:", (chr(addr&0xff),chr(addr>>8)), end=" ")
                    codelist.extend([addr&0xff, addr>>8])
                #     for j in arg[2:]:
                #         codelist.append(j)
                elif 'a' in fmt:
                    arg = opargs[0]
                    i += 1
                    #print("block:", arg[0]|(arg[1]<<8), end=" ")
                    addr = blockaddrs[arg] - i
                    #print("address:", blockaddrs[arg[0]|(arg[1]<<8)], end=" ")
                    #print("offset:", addr, end=" ")
                    #print("encoded:", (chr(addr&0xff),chr(addr>>8)), end=" ")
                    codelist.extend([addr&0xff, addr>>8])
                    for j in arg[2:]:
                        codelist.append(j)
                else:
                    i += 1
                    codelist.append(opargs[0])
                #print

        print(">>>", codelist)
        return bytes(codelist)

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

    def _insure_output(self):
        if self.output is None:
            self.optimize()

    ## bunch of list-like methods ...

    def __getattr__(self, name):
        self._insure_output()
        return getattr(self.output, name)

    def __repr__(self):
        self._insure_output()
        return repr(self.output)

    def __eq__(self, lst):
        self._insure_output()
        if isinstance(lst, type(self.output)):
            return self.output == lst
        return self.output == lst.output

    def __ne__(self, lst):
        self._insure_output()
        if isinstance(lst, type(self.output)):
            return self.output != lst
        return self.output != lst.output

    def __lt__(self, lst):
        self._insure_output()
        if isinstance(lst, type(self.output)):
            return self.output < lst
        return self.output < lst.output

    def __le__(self, lst):
        self._insure_output()
        if isinstance(lst, type(self.output)):
            return self.output <= lst
        return self.output <= lst.output

    def __gt__(self, lst):
        self._insure_output()
        if isinstance(lst, type(self.output)):
            return self.output > lst
        return self.output > lst.output

    def __ge__(self, lst):
        self._insure_output()
        if isinstance(lst, type(self.output)):
            return self.output >= lst
        return self.output >= lst.output

    def __len__(self):
        self._insure_output()
        return len(self.output)

    def __getitem__(self, i):
        self._insure_output()
        return self.output[i]

    def __setitem__(self, i, item):
        self._insure_output()
        self.output[i] = item

    def __delitem__(self, i):
        self._insure_output()
        del self.output[i]

    def __getslice__(self, i, j):
        self._insure_output()
        return self.__class__(self.output[i:j])

    def __setslice__(self, i, j, lst):
        self._insure_output()
        if isinstance(lst, type(self.output)):
            self.output[i:j] = lst
        else:
            self.output[i:j] = lst.output

    def __delslice__(self, i, j):
        self._insure_output()
        del self.output[i:j]

    def append(self, item):
        self._insure_output()
        self.output.append(item)

    def insert(self, i, item):
        self._insure_output()
        self.output.insert(i, item)

    def remove(self, item):
        self._insure_output()
        self.output.remove(item)

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
        # input to this guy is a stack code string - eventually we should
        # be able to deduce this from the code object itself.
        # in the meantime, we fudge by setting opcodes.ISET appropriately
        self.unhandledops = {}
        self.skippedops = {}
        self.stacklevel = code.co_nlocals
        super().__init__(code)
        # Stack starts right after locals. Together, the locals and
        # the space allocated for the stack form a single register
        # file.
        self.max_stacklevel = self.stacklevel + self.code_.co_stacksize
        print(">> nlocals:", self.code_.co_nlocals)
        print(">> stacksize:", self.code_.co_stacksize)
        assert self.max_stacklevel <= 127, "locals+stack are too big!"

    def has_bad_instructions(self):
        assert self.blocks is not None, "need to find blocks first!"
        for block in self.blocks:
            for i in block:
                if i[0] in self.bad_instructions:
                    return True
        return False

    def set_block_stacklevel(self, target, level):
        """set the input stack level for particular block"""
        print(">> set:", (target, level))
        try:
            self.input[target].set_stacklevel(level)
        except IndexError:
            print("!!", target, level, len(self.input))
            raise

    def optimize(self):
        self.unhandledops = {}
        self.skippedops = {}
        #print(">> start:", self.stacklevel)
        OptimizeFilter.optimize(self)

    # series of operations below mimic the stack changes of various
    # stack operations so we know what slot to find particular values in
    def push(self):
        """increment and return next writable slot on the stack"""
        self.stacklevel += 1
        #print(">> push:", self.stacklevel)
        assert self.stacklevel <= self.max_stacklevel, \
            f"Overran the end of the registers! {self.stacklevel} > {self.max_stacklevel}"
        return self.stacklevel - 1

    def pop(self):
        """return top readable slot on the stack and decrement"""
        self.stacklevel -= 1
        #print(">> pop:", self.stacklevel)
        assert self.stacklevel >= self.code_.co_nlocals, \
            f"Stack slammed into locals! {self.stacklevel} < {self.code_.co_nlocals}"
        return self.stacklevel

    def top(self):
        """return top readable slot on the stack"""
        #print(">> top:", self.stacklevel)
        return self.stacklevel

    def set_stacklevel(self, level):
        """set stack level explicitly - used to handle jump targets"""
        if level < self.code_.co_nlocals:
            raise ValueError("invalid stack level: %d" % level)
        self.stacklevel = level
        #print(">> set:", self.stacklevel)
        return self.stacklevel


    @debug_convert
    def unary_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        opname = "%s_REG" % opcodes.ISET.opname[op]
        src = self.pop()
        dst = self.push()
        return [
            (opcodes.ISET.opmap[opname], (dst, src)),
        ]
    dispatch[opcodes.ISET.opmap['UNARY_INVERT']] = unary_convert
    dispatch[opcodes.ISET.opmap['UNARY_POSITIVE']] = unary_convert
    dispatch[opcodes.ISET.opmap['UNARY_NEGATIVE']] = unary_convert
    dispatch[opcodes.ISET.opmap['UNARY_NOT']] = unary_convert

    @debug_convert
    def binary_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        opname = "%s_REG" % opcodes.ISET.opname[op]
        ## TBD... Still not certain I have argument order/byte packing correct.
        # dst <- src1 OP src2
        src1 = self.pop()       # left-hand register src
        src2 = self.pop()       # right-hand register src
        dst = self.push()       # dst
        return [
            (opcodes.ISET.opmap[opname], (dst, src1, src2)),
        ]
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

    def subscript_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['BINARY_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            dst = self.push()
            return [(opcodes.ISET.opmap['BINARY_SUBSCR_REG'],
                     (obj, index, dst))]
        if op == opcodes.ISET.opmap['STORE_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            val = self.pop()
            return [(opcodes.ISET.opmap['STORE_SUBSCR_REG'],
                     (obj, index, val))]
        if op == opcodes.ISET.opmap['DELETE_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            return [(opcodes.ISET.opmap['DELETE_SUBSCR_REG'],
                     (obj, index))]
        return None
    dispatch[opcodes.ISET.opmap['BINARY_SUBSCR']] = subscript_convert
    dispatch[opcodes.ISET.opmap['STORE_SUBSCR']] = subscript_convert
    dispatch[opcodes.ISET.opmap['DELETE_SUBSCR']] = subscript_convert

    def function_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['CALL_FUNCTION']:
            na = oparg[0]
            nk = oparg[1]
            src = self.top()
            for _ in range(na):
                src = self.pop()
            for _ in range(nk*2):
                src = self.pop()
            return [(opcodes.ISET.opmap['CALL_FUNCTION_REG'],
                     (na, nk, src))]
        # TBD - BUILD_CLASS is gone
        # if op == opcodes.ISET.opmap['BUILD_CLASS']:
        #     u = self.pop()
        #     v = self.pop()
        #     w = self.pop()
        #     return (opcodes.ISET.opmap['BUILD_CLASS_REG'], (u, v, w))
        if op == opcodes.ISET.opmap['MAKE_FUNCTION']:
            code = self.pop()
            n = oparg[0]|(oparg[1]<<8)
            dst = self.push()
            return [(opcodes.ISET.opmap['MAKE_FUNCTION_REG'],
                     (code, n, dst))]
        return None
    dispatch[opcodes.ISET.opmap['MAKE_FUNCTION']] = function_convert
    dispatch[opcodes.ISET.opmap['CALL_FUNCTION']] = function_convert
    # dispatch[opcodes.ISET.opmap['BUILD_CLASS']] = function_convert

    @debug_convert
    def jump_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        retval = None
        opname = f"{opcodes.ISET.opname[op]}_REG"
        if op == opcodes.ISET.opmap['RETURN_VALUE']:
            val = self.pop()
            retval = [
                (opcodes.ISET.opmap[opname], val),
            ]
        elif op in (opcodes.ISET.opmap['POP_JUMP_IF_FALSE'],
                    opcodes.ISET.opmap['POP_JUMP_IF_TRUE']):
            self.set_block_stacklevel(oparg, self.top())
            retval = [
                (opcodes.ISET.opmap[opname], (oparg, self.pop())),
            ]
        elif op in (opcodes.ISET.opmap['JUMP_FORWARD'],
                    opcodes.ISET.opmap['JUMP_ABSOLUTE']):
            self.set_block_stacklevel(oparg, self.top())
            retval = [
                (opcodes.ISET.opmap[opname], oparg),
            ]
        if retval is None:
            print("!!", "Unhandled opcode:", op, oparg)
        return retval
    dispatch[opcodes.ISET.opmap['JUMP_FORWARD']] = jump_convert
    dispatch[opcodes.ISET.opmap['JUMP_ABSOLUTE']] = jump_convert
    dispatch[opcodes.ISET.opmap['POP_JUMP_IF_FALSE']] = jump_convert
    dispatch[opcodes.ISET.opmap['POP_JUMP_IF_TRUE']] = jump_convert
    dispatch[opcodes.ISET.opmap['JUMP_ABSOLUTE']] = jump_convert
    # dispatch[opcodes.ISET.opmap['FOR_LOOP']] = jump_convert
    # dispatch[opcodes.ISET.opmap['SETUP_LOOP']] = jump_convert
    dispatch[opcodes.ISET.opmap['RETURN_VALUE']] = jump_convert
    # dispatch[opcodes.ISET.opmap['BREAK_LOOP']] = jump_convert

    @debug_convert
    def load_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['LOAD_FAST']:
            src = oparg[0]         # offset into localsplus
            dst = self.push()      # unused
            print("///", op, dst, src)
            return [
                (opcodes.ISET.opmap['LOAD_FAST_REG'], (dst, src)),
            ]
        if op == opcodes.ISET.opmap['LOAD_CONST']:
            src = oparg         # reference into co_consts
            dst = self.push()   # offset into localsplus
            return [
                (opcodes.ISET.opmap['LOAD_CONST_REG'], (dst, src)),
            ]
        if op == opcodes.ISET.opmap['LOAD_GLOBAL']:
            src = oparg         # global name to be found
            dst = self.push()   # offset into localsplus
            return [
                (opcodes.ISET.opmap['LOAD_GLOBAL_REG'], (dst, src)),
            ]
        return None
    dispatch[opcodes.ISET.opmap['LOAD_CONST']] = load_convert
    dispatch[opcodes.ISET.opmap['LOAD_GLOBAL']] = load_convert
    dispatch[opcodes.ISET.opmap['LOAD_FAST']] = load_convert

    def store_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['STORE_FAST']:
            src = oparg
            dst = self.pop()
            return [
                (opcodes.ISET.opmap['STORE_FAST_REG'], (dst, src)),
            ]
        if op == opcodes.ISET.opmap['STORE_GLOBAL']:
            src = oparg
            dst = self.pop()
            return [
                (opcodes.ISET.opmap['STORE_GLOBAL_REG'], (dst, src)),
            ]
        return None
    dispatch[opcodes.ISET.opmap['STORE_FAST']] = store_convert
    dispatch[opcodes.ISET.opmap['STORE_GLOBAL']] = store_convert

    def attr_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['LOAD_ATTR']:
            obj = self.pop()
            attr = oparg
            dst = self.push()
            return [
                (opcodes.ISET.opmap['LOAD_ATTR_REG'], (dst, obj, attr)),
            ]
        if op == opcodes.ISET.opmap['STORE_ATTR']:
            obj = self.pop()
            attr = oparg
            val = self.pop()
            return [
                (opcodes.ISET.opmap['STORE_ATTR_REG'], (obj, attr, val)),
            ]
        if op == opcodes.ISET.opmap['DELETE_ATTR']:
            obj = self.pop()
            attr = oparg
            return [
                (opcodes.ISET.opmap['DELETE_ATTR_REG'], (obj, attr)),
            ]
        return None
    dispatch[opcodes.ISET.opmap['STORE_ATTR']] = attr_convert
    dispatch[opcodes.ISET.opmap['DELETE_ATTR']] = attr_convert
    dispatch[opcodes.ISET.opmap['LOAD_ATTR']] = attr_convert

    def seq_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['BUILD_MAP']:
            dst = self.push()
            return [
                (opcodes.ISET.opmap['BUILD_MAP_REG'], dst),
            ]
        opname = "%s_REG" % opcodes.ISET.opname[op]
        if op in (opcodes.ISET.opmap['BUILD_LIST'],
                     opcodes.ISET.opmap['BUILD_TUPLE']):
            n = oparg
            for _ in range(n):
                self.pop()
            src = self.top()
            dst = self.push()
            return [
                (opcodes.ISET.opmap[opname], (dst, n, src)),
            ]
        if op == opcodes.ISET.opmap['UNPACK_SEQUENCE']:
            n = oparg
            src = self.pop()
            for _ in range(n):
                self.push()
            return [
                (opcodes.ISET.opmap[opname], (n, src)),
            ]
        return None
    dispatch[opcodes.ISET.opmap['BUILD_TUPLE']] = seq_convert
    dispatch[opcodes.ISET.opmap['BUILD_LIST']] = seq_convert
    dispatch[opcodes.ISET.opmap['BUILD_MAP']] = seq_convert
    dispatch[opcodes.ISET.opmap['UNPACK_SEQUENCE']] = seq_convert

    @debug_convert
    def compare_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['COMPARE_OP']:
            cmpop = oparg
            src2 = self.pop()
            src1 = self.pop()
            dst = self.push()
            return [
                (opcodes.ISET.opmap['COMPARE_OP_REG'], (dst, src1, src2, cmpop)),
            ]
        return None
    dispatch[opcodes.ISET.opmap['COMPARE_OP']] = compare_convert

    @debug_convert
    def stack_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['POP_TOP']:
            self.pop()
            return []
        if op == opcodes.ISET.opmap['DUP_TOP']:
            # nop
            _dummy = self.top()
            _dummy = self.push()
            return []
        if op == opcodes.ISET.opmap['ROT_TWO']:
            a = self.top()
            return [
                (opcodes.ISET.opmap['ROT_TWO_REG'], a),
            ]
        if op == opcodes.ISET.opmap['ROT_THREE']:
            a = self.top()
            return [
                (opcodes.ISET.opmap['ROT_THREE_REG'], a),
            ]
        if op == opcodes.ISET.opmap['POP_BLOCK']:
            return [
                (opcodes.ISET.opmap['POP_BLOCK_REG'], 0),
            ]
        return None
    dispatch[opcodes.ISET.opmap['POP_TOP']] = stack_convert
    dispatch[opcodes.ISET.opmap['ROT_TWO']] = stack_convert
    dispatch[opcodes.ISET.opmap['ROT_THREE']] = stack_convert
    dispatch[opcodes.ISET.opmap['DUP_TOP']] = stack_convert
    dispatch[opcodes.ISET.opmap['POP_BLOCK']] = stack_convert

    def misc_convert(self, instr):
        op, oparg = instr
        oparg = oparg[0]        # All PyVM opcodes have a single oparg
        if op == opcodes.ISET.opmap['IMPORT_NAME']:
            dst = self.push()
            return [
                (opcodes.ISET.opmap['IMPORT_NAME_REG'], (dst, oparg[0])),
            ]
        opname = "%s_REG" % opcodes.ISET.opname[op]
        if op == opcodes.ISET.opmap['PRINT_EXPR']:
            src = self.pop()
            return [
                (opcodes.ISET.opmap[opname], src),
            ]
        return None
    dispatch[opcodes.ISET.opmap['IMPORT_NAME']] = misc_convert
    dispatch[opcodes.ISET.opmap['PRINT_EXPR']] = misc_convert

    @debug_method
    def optimize_block(self, block):
        #print(">> block:", block.block)
        block_stacklevel = block.get_stacklevel()
        if block_stacklevel != -1:
            self.set_stacklevel(block_stacklevel)
        newblock = Block()
        for i in block:
            op = i[0]
            #oparg = i[1]
            #print(">>", opcodes.ISET.opname[op], op, oparg)
            newops = self.dispatch[op](self, i)
            if newops is None:
                try:
                    self.unhandledops[op] += + 1
                except KeyError:
                    print("unhandled", opcodes.ISET.opname[op])
                    self.unhandledops[op] = 1
            else:
                newblock.extend(newops)
        result = []
        for (opcode, oparg) in newblock.block:
            result.append((opcodes.ISET.opname[opcode], oparg))
        print(">> newblock:", result)
        return newblock


def f(a):
    return a + 4

def main():
    isc = InstructionSetConverter(f.__code__)
    isc.find_blocks()
    isc.gen_instructions()
    isc.convert_instructions()
    isc.forward_propagate_reads()
    isc.reverse_propagate_writes()
    if isc.has_bad_instructions():
        # wasn't able to convert, because there are bad instructions
        # in the input
        print(">> Some instructions can't be converted.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
