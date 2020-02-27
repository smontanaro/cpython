"""
### NOTE: This comes from the old Rattlesnake compiler. It's useful
### here initially as documentation of how I did things way back
### when. The more I struggle with the current compiler, the more I
### think I will revert to this method.
"""

import dis
import importlib
import math
import os
#import pprint
import sys
import types

# TBD... will change at some point
import regopcodes as opcodes

__version__ = "0.3"

# varying stages of optimization - which is called is determined
# later by the value of the OPTLEVEL environment variable

def optimize0(code):
    "no-op(timize)"
    return code


def optimize5(code):
    """optimize code object, returning tuple (code object, new_instr)"""
    isc = InstructionSetConverter(code)
    if isc.has_bad_instructions():
        # wasn't able to convert, because there are bad instructions
        # in the input
        return code.co_code
    return isc.code()

class Block:
    """represent a block of code with a single entry point (first instr)"""
    def __init__(self):
        print(f">> new block {hex(id(self))}")
        self.block = []
        self.stacklevel = -1

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
        self.code_ = code
        self.iset = opcodes.stack
        if isinstance(code, types.CodeType):
            self.input = self.blocks(code.co_code)
            self.varnames = code.co_varnames
            self.names = code.co_names
            self.constants = code.co_consts
        else:
            self.input = self.blocks(code)
            self.varnames = self.input.varnames
            self.names = self.input.names
            self.constants = self.input.constants

        self.output = None

    def namify(self, block):
        """return block with names in place of opcodes (debug routine)"""
        block = list(block)
        for i in range(len(block)):
            block[i] = (opcodes.stack.opname[block[i][0]],) + block[i][1:]
        return tuple(block)

    def findlabels(self, code):
        #print(">>", code)
        labels = {0}
        n = len(code)
        i = 0
        while i < n:
            op = code[i]
            opname = opcodes.stack.opname[op]
            fmt = self.iset.format(op)
            print("findlabel:", i, opname, "fmt:", repr(fmt), end=" ")
            nbytes = len(fmt)
            if nbytes == 1:
                addr = code[i+1]
                i += 2
            else:
                assert nbytes == 3, (nbytes, opname, fmt, nbytes)
                addr = code[i+1] | code[i+2] << 8 | code[i+3] << 16
                i += 4
            print(f"addr == {addr}")
            if 'a' in fmt:
                # relative jump
                labels.add(i + addr)
                print(i, "labels:", labels)
            elif 'A' in fmt:
                # abs jump
                labels.add(addr)
                print(i, "labels:", labels)
        labels = sorted(labels)
        #print(">> labels (OptimizeFilter.findlabels):", labels)
        return labels

    def optimize(self):
        """Optimize each block in the input blocks."""
        blocks = self.input
        self.output = [None]*len(blocks)
        for i in range(len(blocks)):
            self.output[i] = self.optimize_block(blocks[i])

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

    def blocks(self, code):
        """Convert code string to block form."""
        blocks = []
        labels = self.findlabels(code)
        #print(">>> labels:", labels)
        n = len(code)
        i = 0
        while i < n:
            if i in labels:
                blocks.append(Block())
            op = code[i]
            opname = opcodes.stack.opname[op]
            oparg = code[i+1]
            block = blocks[-1]
            fmt = self.iset.format(op)
            if opcodes.stack.has_argument(op):
                try:
                    if 'A' in fmt:
                        idx = labels.index(oparg)
                        print(f"  {i:4d} append: {opname} {op} {idx}")
                        blocks[-1].append((op, (idx, 0)))
                    elif 'a' in fmt:
                        idx = labels.index(i+2+oparg)
                        print(f"  {i:4d} append: {opname} {op} {idx}")
                        blocks[-1].append((op, (idx, 0)))
                    else:
                        print(f"  {i:4d} append: {opname} {op} {oparg}")
                        blocks[-1].append((op, oparg))
                except ValueError:
                    print(">>", labels)
                    raise
            else:
                assert oparg == 0
                print(f"  {i:4d} append: {opname} {op} {oparg}")
                blocks[-1].append((op, oparg))
            i += 2
        return blocks

    def code(self):
        """Convert the block form of the code back to a string."""
        self._insure_output()
        blockaddrs = [0]
        blockaddr = 0
        for block in self.output:
            blockaddrs.append(blocklength(block)+blockaddrs[-1])

        #print(">>> block addresses:", blockaddrs)
        #for i in range(len(self.output)):
            #print(">> block:", i, "address:", blockaddrs[i])
            #pprint.pprint(self.namify(self.output[i]))

        codelist = [self.iset.opmap['NEW_VM_REG']]
        i = 1
        for block in self.output:
            try:
                for inst in block:
                    op = chr(inst[0])
                    codelist.append(op)
                    fmt = self.iset.format(inst[0])
                    #print(">>", (i, self.iset.opname[inst[0]], fmt), end=" ")
                    i = i + 1
                    if 'A' in fmt:
                        arg = inst[1]
                        i = i + len(arg)
                        #print("block:", arg[0]|(arg[1]<<8), end=" ")
                        addr = blockaddrs[arg[0]|(arg[1]<<8)]
                        #print("address:", addr, end=" ")
                        #print("encoded:", (chr(addr&0xff),chr(addr>>8)), end=" ")
                        codelist.append("%s%s" %
                                        (chr(addr&0xff), chr(addr>>8)))
                        for j in arg[2:]:
                            codelist.append(chr(j))
                    elif 'a' in fmt:
                        arg = inst[1]
                        i = i + len(arg)
                        #print("block:", arg[0]|(arg[1]<<8), end=" ")
                        addr = blockaddrs[arg[0]|(arg[1]<<8)]-i
                        #print("address:", blockaddrs[arg[0]|(arg[1]<<8)], end=" ")
                        #print("offset:", addr, end=" ")
                        #print("encoded:", (chr(addr&0xff),chr(addr>>8)), end=" ")
                        codelist.append("%s%s" %
                                        (chr(addr&0xff), chr(addr>>8)))
                        for j in arg[2:]:
                            codelist.append(chr(j))
                    else:
                        i = i + len(inst[1])
                        for arg in inst[1]:
                            codelist.append(chr(arg))
                    #print
            except ValueError:
                print((opcodes.stack.opname[inst[0]], inst[1:],
                       i, blockaddrs[blockaddr]))
                raise

        # TBD... This is certainly incorrect. the input and output code strings are byte strings.
        return "".join(codelist)

    def constant_value(self, op):
        if op[0] == opcodes.stack.opmap["LOAD_CONST"]:
            return self.constants[op[1][0]+(op[1][1]<<8)]
        if op[0] == opcodes.stack.opmap["LOADI"]:
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
    bad_instructions = {opcodes.stack.opmap['LOAD_NAME']:1,
                        opcodes.stack.opmap['STORE_NAME']:1,
                        opcodes.stack.opmap['DELETE_NAME']:1,
                        opcodes.stack.opmap['SETUP_FINALLY']:1,
                        opcodes.stack.opmap['IMPORT_FROM']:1}
    dispatch = {}

    def __init__(self, code):
        # input to this guy is a stack code string - eventually we should
        # be able to deduce this from the code object itself.
        # in the meantime, we fudge by setting self.iset appropriately
        self.iset = opcodes.stack
        self.unhandledops = {}
        self.skippedops = {}
        self.stacklevel = 0
        OptimizeFilter.__init__(self, code)
        self.iset = opcodes.register

    def namify(self, block):
        """return block with names in place of opcodes (debug routine)"""
        block = list(block)
        for i in range(len(block)):
            block[i] = (self.iset.opname[block[i][0]],) + block[i][1:]
        return tuple(block)

    def has_bad_instructions(self):
        blocks = self.blocks(self.code_.co_code)
        for block in blocks:
            for i in block:
                if i[0] in self.bad_instructions:
                    return True
        return False

    def set_block_stacklevel(self, id_, level):
        """set the input stack level for particular block"""
        print(">> set:", (id_, level))
        try:
            self.input[id_].set_stacklevel(level)
        except IndexError:
            # print("!!", id_, level, len(self.input),
            #       [inp.block for inp in self.input])
            raise

    def optimize(self):
        self.stacklevel = self.code_.co_nlocals
        self.unhandledops = {}
        self.skippedops = {}
        #print(">> start:", self.stacklevel)
        OptimizeFilter.optimize(self)

    # series of operations below mimic the stack changes of various
    # stack operations so we know what slot to find particular values in
    def push(self):
        """increment and return next writable slot on the stack"""
        self.stacklevel = self.stacklevel + 1
        #print(">> push:", self.stacklevel)
        return self.stacklevel - 1

    def pop(self):
        """return top readable slot on the stack and decrement"""
        self.stacklevel = self.stacklevel - 1
        #print(">> pop:", self.stacklevel)
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


    def unary_convert(self, op):
        opname = "%s_REG" % opcodes.stack.opname[op[0]]
        src = self.pop()
        dst = self.push()
        return (opcodes.register.opmap[opname], (src, dst))
    dispatch[opcodes.stack.opmap['UNARY_INVERT']] = unary_convert
    dispatch[opcodes.stack.opmap['UNARY_POSITIVE']] = unary_convert
    dispatch[opcodes.stack.opmap['UNARY_NEGATIVE']] = unary_convert
    dispatch[opcodes.stack.opmap['UNARY_NOT']] = unary_convert

    def binary_convert(self, op):
        opname = "%s_REG" % opcodes.stack.opname[op[0]]
        src2 = self.pop()
        src1 = self.pop()
        dst = self.push()
        return (opcodes.register.opmap[opname], (src1, src2, dst))
    dispatch[opcodes.stack.opmap['BINARY_POWER']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_MULTIPLY']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_MATRIX_MULTIPLY']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_TRUE_DIVIDE']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_FLOOR_DIVIDE']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_MODULO']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_ADD']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_SUBTRACT']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_LSHIFT']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_RSHIFT']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_AND']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_XOR']] = binary_convert
    dispatch[opcodes.stack.opmap['BINARY_OR']] = binary_convert

    def subscript_convert(self, op):
        if op[0] == opcodes.stack.opmap['BINARY_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            dst = self.push()
            return (opcodes.register.opmap['BINARY_SUBSCR_REG'],
                    (obj, index, dst))
        if op[0] == opcodes.stack.opmap['STORE_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            val = self.pop()
            return (opcodes.register.opmap['STORE_SUBSCR_REG'],
                    (obj, index, val))
        if op[0] == opcodes.stack.opmap['DELETE_SUBSCR']:
            index = self.pop()
            obj = self.pop()
            return (opcodes.register.opmap['DELETE_SUBSCR_REG'],
                    (obj, index))
        return None
    dispatch[opcodes.stack.opmap['BINARY_SUBSCR']] = subscript_convert
    dispatch[opcodes.stack.opmap['STORE_SUBSCR']] = subscript_convert
    dispatch[opcodes.stack.opmap['DELETE_SUBSCR']] = subscript_convert

    def function_convert(self, op):
        if op[0] == opcodes.stack.opmap['CALL_FUNCTION']:
            na = op[1][0]
            nk = op[1][1]
            src = self.top()
            for _ in range(na):
                src = self.pop()
            for _ in range(nk*2):
                src = self.pop()
            return (opcodes.register.opmap['CALL_FUNCTION_REG'],
                    (na, nk, src))
        # TBD - BUILD_CLASS is gone
        # if op[0] == opcodes.stack.opmap['BUILD_CLASS']:
        #     u = self.pop()
        #     v = self.pop()
        #     w = self.pop()
        #     return (opcodes.register.opmap['BUILD_CLASS_REG'], (u, v, w))
        if op[0] == opcodes.stack.opmap['MAKE_FUNCTION']:
            code = self.pop()
            n = op[1][0]|(op[1][1]<<8)
            dst = self.push()
            return (opcodes.register.opmap['MAKE_FUNCTION_REG'],
                    (code, n, dst))
        return None
    dispatch[opcodes.stack.opmap['MAKE_FUNCTION']] = function_convert
    dispatch[opcodes.stack.opmap['CALL_FUNCTION']] = function_convert
    # dispatch[opcodes.stack.opmap['BUILD_CLASS']] = function_convert

    def jump_convert(self, op):
        retval = None
        opname = f"{opcodes.stack.opname[op[0]]}_REG"
        if op[0] == opcodes.stack.opmap['RETURN_VALUE']:
            val = self.pop()
            retval = (opcodes.register.opmap[opname], (val,))
        elif op[0] == opcodes.stack.opmap['POP_JUMP_IF_FALSE']:
            tgt = op[1]
            self.set_block_stacklevel(tgt, self.top())
            retval = (opcodes.register.opmap[opname], (tgt, self.top()))
        elif op[0] == opcodes.stack.opmap['POP_JUMP_IF_TRUE']:
            tgt = op[1]
            self.set_block_stacklevel(tgt, self.top())
            retval = (opcodes.register.opmap[opname], (tgt, self.top()))
        else:
            if op[0] in (opcodes.stack.opmap['JUMP_FORWARD'],
                         opcodes.stack.opmap['JUMP_ABSOLUTE']):
                tgt = op[1]
                self.set_block_stacklevel(tgt, self.top())
                retval = (opcodes.register.opmap[opname], (tgt,))
        if retval is None:
            print("!!", "Unhandled opcode:", op)
        return retval
    dispatch[opcodes.stack.opmap['JUMP_FORWARD']] = jump_convert
    dispatch[opcodes.stack.opmap['JUMP_ABSOLUTE']] = jump_convert
    dispatch[opcodes.stack.opmap['POP_JUMP_IF_FALSE']] = jump_convert
    dispatch[opcodes.stack.opmap['POP_JUMP_IF_TRUE']] = jump_convert
    dispatch[opcodes.stack.opmap['JUMP_ABSOLUTE']] = jump_convert
    # dispatch[opcodes.stack.opmap['FOR_LOOP']] = jump_convert
    # dispatch[opcodes.stack.opmap['SETUP_LOOP']] = jump_convert
    dispatch[opcodes.stack.opmap['RETURN_VALUE']] = jump_convert
    # dispatch[opcodes.stack.opmap['BREAK_LOOP']] = jump_convert

    def load_convert(self, op):
        if op[0] == opcodes.stack.opmap['LOAD_FAST']:
            src = op[1]
            dst = self.push()
            return (opcodes.register.opmap['LOAD_FAST_REG'], (src, dst))
        if op[0] == opcodes.stack.opmap['LOAD_CONST']:
            src = op[1]
            dst = self.push()
            return (opcodes.register.opmap['LOAD_CONST_REG'], (src, dst))
        if op[0] == opcodes.stack.opmap['LOAD_GLOBAL']:
            src = op[1]
            dst = self.push()
            return (opcodes.register.opmap['LOAD_GLOBAL_REG'], (src, dst))
        return None
    dispatch[opcodes.stack.opmap['LOAD_CONST']] = load_convert
    dispatch[opcodes.stack.opmap['LOAD_GLOBAL']] = load_convert
    dispatch[opcodes.stack.opmap['LOAD_FAST']] = load_convert

    def store_convert(self, op):
        if op[0] == opcodes.stack.opmap['STORE_FAST']:
            dst = op[1]
            src = self.pop()
            return (opcodes.register.opmap['LOAD_FAST_REG'], (src, dst))
        if op[0] == opcodes.stack.opmap['STORE_GLOBAL']:
            dst = op[1]
            src = self.pop()
            return (opcodes.register.opmap['STORE_GLOBAL_REG'], (src, dst))
        return None
    dispatch[opcodes.stack.opmap['STORE_FAST']] = store_convert
    dispatch[opcodes.stack.opmap['STORE_GLOBAL']] = store_convert

    def attr_convert(self, op):
        if op[0] == opcodes.stack.opmap['LOAD_ATTR']:
            obj = self.pop()
            attr = op[1]
            dst = self.push()
            return (opcodes.register.opmap['LOAD_ATTR_REG'], (obj, attr, dst))
        if op[0] == opcodes.stack.opmap['STORE_ATTR']:
            obj = self.pop()
            attr = op[1]
            val = self.pop()
            return (opcodes.register.opmap['STORE_ATTR_REG'], (obj, attr, val))
        if op[0] == opcodes.stack.opmap['DELETE_ATTR']:
            obj = self.pop()
            attr = op[1]
            return (opcodes.register.opmap['DELETE_ATTR_REG'], (obj, attr))
        return None
    dispatch[opcodes.stack.opmap['STORE_ATTR']] = attr_convert
    dispatch[opcodes.stack.opmap['DELETE_ATTR']] = attr_convert
    dispatch[opcodes.stack.opmap['LOAD_ATTR']] = attr_convert

    def seq_convert(self, op):
        if op[0] == opcodes.stack.opmap['BUILD_MAP']:
            dst = self.push()
            return (opcodes.register.opmap['BUILD_MAP_REG'], (dst,))
        opname = "%s_REG" % opcodes.stack.opname[op[0]]
        if op[0] in (opcodes.stack.opmap['BUILD_LIST'],
                     opcodes.stack.opmap['BUILD_TUPLE']):
            n = op[1]
            for _ in range(n):
                self.pop()
            src = self.top()
            dst = self.push()
            return (opcodes.register.opmap[opname], (n, src, dst))
        if op[0] == opcodes.stack.opmap['UNPACK_SEQUENCE']:
            n = op[1]
            src = self.pop()
            for _ in range(n):
                self.push()
            return (opcodes.register.opmap[opname], (n, src))
        return None
    dispatch[opcodes.stack.opmap['BUILD_TUPLE']] = seq_convert
    dispatch[opcodes.stack.opmap['BUILD_LIST']] = seq_convert
    dispatch[opcodes.stack.opmap['BUILD_MAP']] = seq_convert
    dispatch[opcodes.stack.opmap['UNPACK_SEQUENCE']] = seq_convert

    def compare_convert(self, op):
        if op[0] == opcodes.stack.opmap['COMPARE_OP']:
            cmpop = op[1]
            src2 = self.pop()
            src1 = self.pop()
            dst = self.push()
            return (opcodes.register.opmap['COMPARE_OP_REG'],
                    (src1, src2, cmpop, dst))
        return None
    dispatch[opcodes.stack.opmap['COMPARE_OP']] = compare_convert

    def stack_convert(self, op):
        if op[0] == opcodes.stack.opmap['POP_TOP']:
            self.pop()
            return ()
        if op[0] == opcodes.stack.opmap['DUP_TOP']:
            src = self.top()
            dst = self.push()
            return (opcodes.register.opmap['LOAD_FAST_REG'], (src, dst))
        if op[0] == opcodes.stack.opmap['ROT_TWO']:
            a = self.top()
            return (opcodes.register.opmap['ROT_TWO_REG'], (a,))
        if op[0] == opcodes.stack.opmap['ROT_THREE']:
            a = self.top()
            return (opcodes.register.opmap['ROT_THREE_REG'], (a,))
        if op[0] == opcodes.stack.opmap['POP_BLOCK']:
            return (opcodes.register.opmap['POP_BLOCK_REG'], ())
        return None
    dispatch[opcodes.stack.opmap['POP_TOP']] = stack_convert
    dispatch[opcodes.stack.opmap['ROT_TWO']] = stack_convert
    dispatch[opcodes.stack.opmap['ROT_THREE']] = stack_convert
    dispatch[opcodes.stack.opmap['DUP_TOP']] = stack_convert
    dispatch[opcodes.stack.opmap['POP_BLOCK']] = stack_convert

    def misc_convert(self, op):
        if op[0] == opcodes.stack.opmap['IMPORT_NAME']:
            dst = self.push()
            return (opcodes.register.opmap['IMPORT_NAME_REG'], (op[1][0], dst))
        opname = "%s_REG" % opcodes.stack.opname[op[0]]
        if op[0] == opcodes.stack.opmap['PRINT_EXPR']:
            src = self.pop()
            return (opcodes.register.opmap[opname], (src,))
        return None
    dispatch[opcodes.stack.opmap['IMPORT_NAME']] = misc_convert
    dispatch[opcodes.stack.opmap['PRINT_EXPR']] = misc_convert

    def optimize_block(self, block):
        #print(">> block:", block.block)
        block_stacklevel = block.get_stacklevel()
        if block_stacklevel != -1:
            self.set_stacklevel(block_stacklevel)
        newblock = Block()
        for i in block:
            op = i[0]
            oparg = i[1]
            #print(">>", opcodes.stack.opname[op], op, oparg)
            newop = self.dispatch[op](self, i)
            if newop is None:
                try:
                    self.unhandledops[op] += + 1
                except KeyError:
                    print("unhandled", opcodes.stack.opname[op])
                    self.unhandledops[op] = 1
            elif newop:
                newblock.append(newop)
        print(">> newblock:", newblock.block)
        return newblock


def is_jump(op):
    return op in opcodes.stack.jumps

def is_abs_jump(op):
    return op in opcodes.stack.abs_jumps

def blocklength(block):
    bl = 0
    for insn in block:
        bl = bl + 1
        try:
            bl = bl + len(insn[1])
        except IndexError:
            pass
    return bl



# def test():
#     stdout = sys.stdout
#     import pystone
#     orig = open('pystone.out', 'w')
#     opt = open('pystone.opt', 'w')
#     for n in dir(pystone):
#         f = getattr(pystone, n)
#         if type(f) == type(pystone.Proc0):
#             code = f.__code__.co_code
#             varnames = f.__code__.co_varnames
#             names = f.__code__.co_names
#             constants = f.__code__.co_consts
#             sys.stdout = orig
#             print("\n===Function %s:\n" % n)
#             dis.dis(f)
#             sys.stdout = opt
#             print("\n===Function %s:\n" % n)
#             code = optimize(code, varnames, names, constants)
#             dis.disassemble_string(code,
#                                    varnames=varnames,
#                                    names=names,
#                                    constants=constants)
#     sys.stdout = stdout


def f(a):
    b = a * 8.0
    if b > 24.5:
        b = b / 2
    else:
        b = b * 3
    result = []
    for i in range(int(b)):
        result.append(math.sin(i))
    class FooClass:
        "doc"
    return (FooClass, result)


def test_handle(func):
    print("*"*25, func.__name__, "*"*25)
    print("Stack version:")
    dis.dis(func)
    isg = InstructionSetConverter(func.__code__)
    isg.optimize()
    print()
    print("Register version:")
    dis.dis(isg.code())

def test1(mod=os):
    test_handle(f)
    for k in mod.__dict__:
        func = mod.__dict__[k]
        if isinstance(func, types.FunctionType):
            test_handle(func)

OPTFUNCS = {
    0: optimize0,
    5: optimize5,
}
OPTLEVEL = os.environ.get('OPTLEVEL', "0")
optimize = OPTFUNCS.get(OPTLEVEL, 0)

def main():
    for name in sys.argv[1:]:
        mod = importlib.import_module(name)
        test1(mod)
    return 0

if __name__ == "__main__":
    sys.exit(main())
