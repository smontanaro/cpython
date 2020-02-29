
"""opcodes module - shared between dis and optimize"""

# range of small_int cache - values must match with those used by intobject.c
NSMALLPOSINTS = 100
NSMALLNEGINTS = 1

cmp_op = ('<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is',
          'is not', 'exception match', 'BAD')

class InstructionSet:
    def __init__(self):
        self.opname = [''] * 256
        for op in range(256):
            self.opname[op] = '<' + repr(op) + '>'
        self.opmap = {}
        self.argsmap = {}
        self.jumps = set()
        self.abs_jumps = set()
        self.rel_jumps = set()

    def def_op(self, name, op, argfmt):
        """Associate an opcode with a name & describe arguments.

        Note: In the wordcode system (stack instruction set) each
        instruction has a one-byte oparg. In the quadcode system
        (register instruction set) each instruction has three one-byte
        args (trailing 0 for all unused args).

        Argfmt's contents interpret each byte's functionality.  The
        different characters in an argfmt mean:

        < - comparison operator
        ? - unknown (just a placeholder to get the byte count correct...)
        A - absolute bytecode address
        a - relative bytecode address
        c - index in constant list
        I - literal integer
        i - index in small ints cache
        L - line number
        n - index in name list
        r - index in register (or register+stack for 3-addr instructions)
        0 - unused byte

        """
        self.opmap[name] = op
        self.opname[op] = name
        self.argsmap[op] = argfmt
        if 'a' in argfmt:
            self.jumps.add(op)
            self.rel_jumps.add(op)
        if 'A' in argfmt:
            self.jumps.add(op)
            self.abs_jumps.add(op)

    def argbytes(self, op):
        try:
            return len(self.argsmap[op])
        except KeyError:
            print(">> no opcode:", op, oct(op))
            raise

    def format(self, op):
        try:
            return self.argsmap[op]
        except KeyError:
            print(">> no opcode:", op, oct(op))
            print(">> argsmap keys:", list(self.argsmap.keys()))
            raise

class StackInstructionSet(InstructionSet):
    def has_argument(self, op):
        return op > 90


class RegisterInstructionSet(InstructionSet):
    def has_argument(self, _op):
        # TBD...
        return True

    def def_op(self, name, op, argfmt):
        assert len(argfmt) == 3
        return InstructionSet.def_op(self, name, op, argfmt)

op = 0

stack = StackInstructionSet()
#               name                    opcode          args
stack.def_op('POP_TOP', op, "0") ; op += 1
stack.def_op('ROT_TWO', op, "0") ; op += 1
stack.def_op('ROT_THREE', op, "0") ; op += 1
stack.def_op('DUP_TOP', op, "0") ; op += 1
stack.def_op('DUP_TOP_TWO', op, "0") ; op += 1
stack.def_op('ROT_FOUR', op, "0") ; op += 1
stack.def_op('NOP', op, "0") ; op += 1
stack.def_op('UNARY_POSITIVE', op, "0") ; op += 1
stack.def_op('UNARY_NEGATIVE', op, "0") ; op += 1
stack.def_op('UNARY_NOT', op, "0") ; op += 1
stack.def_op('UNARY_INVERT', op, "0") ; op += 1
stack.def_op('BINARY_MATRIX_MULTIPLY', op, "0") ; op += 1
stack.def_op('INPLACE_MATRIX_MULTIPLY', op, "0") ; op += 1
stack.def_op('BINARY_POWER', op, "0") ; op += 1
stack.def_op('BINARY_MULTIPLY', op, "0") ; op += 1
stack.def_op('BINARY_MODULO', op, "0") ; op += 1
stack.def_op('BINARY_ADD', op, "0") ; op += 1
stack.def_op('BINARY_SUBTRACT', op, "0") ; op += 1
stack.def_op('BINARY_SUBSCR', op, "0") ; op += 1
stack.def_op('BINARY_FLOOR_DIVIDE', op, "0") ; op += 1
stack.def_op('BINARY_TRUE_DIVIDE', op, "0") ; op += 1
stack.def_op('INPLACE_FLOOR_DIVIDE', op, "0") ; op += 1
stack.def_op('INPLACE_TRUE_DIVIDE', op, "0") ; op += 1
stack.def_op('RERAISE', op, "0") ; op += 1
stack.def_op('WITH_EXCEPT_START', op, "0") ; op += 1
stack.def_op('GET_AITER', op, "0") ; op += 1
stack.def_op('GET_ANEXT', op, "0") ; op += 1
stack.def_op('BEFORE_ASYNC_WITH', op, "0") ; op += 1
stack.def_op('END_ASYNC_FOR', op, 'a') ; op += 1
stack.def_op('INPLACE_ADD', op, "0") ; op += 1
stack.def_op('INPLACE_SUBTRACT', op, "0") ; op += 1
stack.def_op('INPLACE_MULTIPLY', op, "0") ; op += 1
stack.def_op('INPLACE_MODULO', op, "0") ; op += 1
stack.def_op('STORE_SUBSCR', op, "0") ; op += 1
stack.def_op('DELETE_SUBSCR', op, "0") ; op += 1
stack.def_op('BINARY_LSHIFT', op, "0") ; op += 1
stack.def_op('BINARY_RSHIFT', op, "0") ; op += 1
stack.def_op('BINARY_AND', op, "0") ; op += 1
stack.def_op('BINARY_XOR', op, "0") ; op += 1
stack.def_op('BINARY_OR', op, "0") ; op += 1
stack.def_op('INPLACE_POWER', op, "0") ; op += 1
stack.def_op('GET_ITER', op, "0") ; op += 1
stack.def_op('GET_YIELD_FROM_ITER', op, "0") ; op += 1
stack.def_op('PRINT_EXPR', op, "0") ; op += 1
stack.def_op('LOAD_BUILD_CLASS', op, "0") ; op += 1
stack.def_op('YIELD_FROM', op, "0") ; op += 1
stack.def_op('GET_AWAITABLE', op, "0") ; op += 1
stack.def_op('LOAD_ASSERTION_ERROR', op, "0") ; op += 1
stack.def_op('INPLACE_LSHIFT', op, "0") ; op += 1
stack.def_op('INPLACE_RSHIFT', op, "0") ; op += 1
stack.def_op('INPLACE_AND', op, "0") ; op += 1
stack.def_op('INPLACE_XOR', op, "0") ; op += 1
stack.def_op('INPLACE_OR', op, "0") ; op += 1
stack.def_op('LIST_TO_TUPLE', op, "0") ; op += 1
stack.def_op('RETURN_VALUE', op, "0") ; op += 1
stack.def_op('IMPORT_STAR', op, "0") ; op += 1
stack.def_op('SETUP_ANNOTATIONS', op, "0") ; op += 1
stack.def_op('YIELD_VALUE', op, "0") ; op += 1
stack.def_op('POP_BLOCK', op, "0") ; op += 1
stack.def_op('POP_EXCEPT', op, "0") ; op += 1

# Opcodes from here have an argument

stack.def_op('STORE_NAME', op, 'n') ; op += 1
stack.def_op('DELETE_NAME', op, 'n') ; op += 1
stack.def_op('UNPACK_SEQUENCE', op, 'I') ; op += 1
stack.def_op('FOR_ITER', op, 'a') ; op += 1
stack.def_op('UNPACK_EX', op, '?') ; op += 1
stack.def_op('STORE_ATTR', op, 'n') ; op += 1
stack.def_op('DELETE_ATTR', op, 'n') ; op += 1
stack.def_op('STORE_GLOBAL', op, 'n') ; op += 1
stack.def_op('DELETE_GLOBAL', op, 'n') ; op += 1

stack.def_op('LOAD_CONST', op, 'c') ; op += 1
stack.def_op('LOAD_NAME', op, 'n') ; op += 1
stack.def_op('BUILD_TUPLE', op, 'I') ; op += 1
stack.def_op('BUILD_LIST', op, 'I') ; op += 1
stack.def_op('BUILD_SET', op, 'I') ; op += 1
stack.def_op('BUILD_MAP', op, 'I') ; op += 1
stack.def_op('LOAD_ATTR', op, 'n') ; op += 1

stack.def_op('COMPARE_OP', op, '<') ; op += 1
stack.def_op('IMPORT_NAME', op, 'n') ; op += 1
stack.def_op('IMPORT_FROM', op, 'n') ; op += 1
stack.def_op('JUMP_FORWARD', op, 'a') ; op += 1
stack.def_op('JUMP_IF_FALSE_OR_POP', op, 'A') ; op += 1
stack.def_op('JUMP_IF_TRUE_OR_POP', op, 'A') ; op += 1
stack.def_op('JUMP_ABSOLUTE', op, 'A') ; op += 1
stack.def_op('POP_JUMP_IF_FALSE', op, 'A') ; op += 1
stack.def_op('POP_JUMP_IF_TRUE', op, 'A') ; op += 1
stack.def_op('LOAD_GLOBAL', op, 'n') ; op += 1
stack.def_op('IS_OP', op, '?') ; op += 1
stack.def_op('CONTAINS_OP', op, '?') ; op += 1
stack.def_op('JUMP_IF_NOT_EXC_MATCH', op, 'a') ; op += 1
stack.def_op('SETUP_FINALLY', op, 'a') ; op += 1

stack.def_op('LOAD_FAST', op, 'r') ; op += 1

stack.def_op('STORE_FAST', op, 'r') ; op += 1

stack.def_op('DELETE_FAST', op, 'r') ; op += 1

stack.def_op('RAISE_VARARGS', op, 'I') ; op += 1
stack.def_op('CALL_FUNCTION', op, 'I') ; op += 1
stack.def_op('MAKE_FUNCTION', op, 'I') ; op += 1
stack.def_op('BUILD_SLICE', op, 'I') ; op += 1

stack.def_op('LOAD_CLOSURE', op, '?') ; op += 1

stack.def_op('LOAD_DEREF', op, '?') ; op += 1

stack.def_op('STORE_DEREF', op, '?') ; op += 1

stack.def_op('DELETE_DEREF', op, '?') ; op += 1
stack.def_op('CALL_FUNCTION_KW', op, '?') ; op += 1
stack.def_op('CALL_FUNCTION_EX', op, '?') ; op += 1
stack.def_op('SETUP_WITH', op, '?') ; op += 1
stack.def_op('LIST_APPEND', op, '?') ; op += 1
stack.def_op('SET_ADD', op, '?') ; op += 1
stack.def_op('MAP_ADD', op, '?') ; op += 1

stack.def_op('LOAD_CLASSDEREF', op, '?') ; op += 1

stack.def_op('EXTENDED_ARG', op, 'n') ; op += 1
stack.def_op('SETUP_ASYNC_WITH', op, '?') ; op += 1
stack.def_op('FORMAT_VALUE', op, '?') ; op += 1
stack.def_op('BUILD_CONST_KEY_MAP', op, '?') ; op += 1
stack.def_op('BUILD_STRING', op, '?') ; op += 1
stack.def_op('LOAD_METHOD', op, '?') ; op += 1
stack.def_op('CALL_METHOD', op, '?') ; op += 1
stack.def_op('LIST_EXTEND', op, '?') ; op += 1
stack.def_op('SET_UPDATE', op, '?') ; op += 1
stack.def_op('DICT_MERGE', op, '?') ; op += 1
stack.def_op('DICT_UPDATE', op, '?') ; op += 1

register = RegisterInstructionSet()

register.def_op('BINARY_POWER_REG', op, 'rrr') ; op += 1
register.def_op('BINARY_MULTIPLY_REG', op, 'rrr') ; op += 1
register.def_op('BINARY_MODULO_REG', op, 'rrr') ; op += 1
register.def_op('BINARY_ADD_REG', op, 'rrr') ; op += 1
register.def_op('BINARY_SUBTRACT_REG', op, 'rrr') ; op += 1
register.def_op('BINARY_SUBSCR_REG', op, 'rrr') ; op += 1
register.def_op('BINARY_FLOOR_DIVIDE_REG', op, 'rrr') ; op += 1
register.def_op('BINARY_TRUE_DIVIDE', op, 'rrr') ; op += 1
register.def_op('RETURN_VALUE_REG', op, 'r00') ; op += 1
register.def_op('LOAD_CONST_REG', op, 'rc0') ; op += 1
register.def_op('LOAD_GLOBAL_REG', op, 'nr0') ; op += 1
# # TBD... Rattlesnake had four args. I'm trying not to overflow into
# # another quad word. If I give this opcode a value <= 64 I have room for
# register.def_op('COMPARE_OP_REG', op, '<rr') ; op += 1
# register.def_op('POP_JUMP_IF_FALSE_REG', op, 'A00') ; op += 1
# register.def_op('POP_JUMP_IF_TRUE_REG', op, 'A00') ; op += 1
# register.def_op('LOAD_FAST_REG', op, 'rr0') ; op += 1
# register.def_op('STORE_FAST_REG', op, 'rr0') ; op += 1

import opcode

assert max(opcode.opmap.values()) == op - 1

del opcode, op
