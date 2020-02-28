
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

    # More TBD, I'm sure...
    def jabs_op(self, name, op, argfmt=""):
        self.jumps.add(op)
        self.abs_jumps.add(op)
        return self.def_op(name, op, argfmt)
    def jrel_op(self, name, op, argfmt=""):
        self.jumps.add(op)
        self.rel_jumps.add(op)
        return self.def_op(name, op, argfmt)
    name_op = def_op

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

stack = StackInstructionSet()
#               name                    opcode          args
stack.def_op('POP_TOP', 1, "0")
stack.def_op('ROT_TWO', 2, "0")
stack.def_op('ROT_THREE', 3, "0")
stack.def_op('DUP_TOP', 4, "0")
stack.def_op('DUP_TOP_TWO', 5, "0")
stack.def_op('ROT_FOUR', 6, "0")

stack.def_op('NOP', 9, "0")
stack.def_op('UNARY_POSITIVE', 10, "0")
stack.def_op('UNARY_NEGATIVE', 11, "0")
stack.def_op('UNARY_NOT', 12, "0")

stack.def_op('UNARY_INVERT', 15, "0")

stack.def_op('BINARY_MATRIX_MULTIPLY', 16, "0")
stack.def_op('INPLACE_MATRIX_MULTIPLY', 17, "0")

stack.def_op('BINARY_POWER', 19, "0")
stack.def_op('BINARY_MULTIPLY', 20, "0")

stack.def_op('BINARY_MODULO', 22, "0")
stack.def_op('BINARY_ADD', 23, "0")
stack.def_op('BINARY_SUBTRACT', 24, "0")
stack.def_op('BINARY_SUBSCR', 25, "0")
stack.def_op('BINARY_FLOOR_DIVIDE', 26, "0")
stack.def_op('BINARY_TRUE_DIVIDE', 27, "0")
stack.def_op('INPLACE_FLOOR_DIVIDE', 28, "0")
stack.def_op('INPLACE_TRUE_DIVIDE', 29, "0")

stack.def_op('RERAISE', 48, "0")
stack.def_op('WITH_EXCEPT_START', 49, "0")
stack.def_op('GET_AITER', 50, "0")
stack.def_op('GET_ANEXT', 51, "0")
stack.def_op('BEFORE_ASYNC_WITH', 52, "0")

stack.def_op('END_ASYNC_FOR', 54, 'a')
stack.def_op('INPLACE_ADD', 55, "0")
stack.def_op('INPLACE_SUBTRACT', 56, "0")
stack.def_op('INPLACE_MULTIPLY', 57, "0")

stack.def_op('INPLACE_MODULO', 59, "0")
stack.def_op('STORE_SUBSCR', 60, "0")
stack.def_op('DELETE_SUBSCR', 61, "0")
stack.def_op('BINARY_LSHIFT', 62, "0")
stack.def_op('BINARY_RSHIFT', 63, "0")
stack.def_op('BINARY_AND', 64, "0")
stack.def_op('BINARY_XOR', 65, "0")
stack.def_op('BINARY_OR', 66, "0")
stack.def_op('INPLACE_POWER', 67, "0")
stack.def_op('GET_ITER', 68, "0")
stack.def_op('GET_YIELD_FROM_ITER', 69, "0")

stack.def_op('PRINT_EXPR', 70, "0")
stack.def_op('LOAD_BUILD_CLASS', 71, "0")
stack.def_op('YIELD_FROM', 72, "0")
stack.def_op('GET_AWAITABLE', 73, "0")
stack.def_op('LOAD_ASSERTION_ERROR', 74, "0")
stack.def_op('INPLACE_LSHIFT', 75, "0")
stack.def_op('INPLACE_RSHIFT', 76, "0")
stack.def_op('INPLACE_AND', 77, "0")
stack.def_op('INPLACE_XOR', 78, "0")
stack.def_op('INPLACE_OR', 79, "0")

stack.def_op('LIST_TO_TUPLE', 82, "0")
stack.def_op('RETURN_VALUE', 83, "0")
stack.def_op('IMPORT_STAR', 84, "0")
stack.def_op('SETUP_ANNOTATIONS', 85, "0")
stack.def_op('YIELD_VALUE', 86, "0")
stack.def_op('POP_BLOCK', 87, "0")

stack.def_op('POP_EXCEPT', 89, "0")

# Opcodes from here have an argument

stack.name_op('STORE_NAME', 90, 'n')
stack.name_op('DELETE_NAME', 91, 'n')
stack.def_op('UNPACK_SEQUENCE', 92, 'I')
stack.jrel_op('FOR_ITER', 93, 'a')
stack.def_op('UNPACK_EX', 94, '?')
stack.name_op('STORE_ATTR', 95, 'n')
stack.name_op('DELETE_ATTR', 96, 'n')
stack.name_op('STORE_GLOBAL', 97, 'n')
stack.name_op('DELETE_GLOBAL', 98, 'n')
stack.def_op('LOAD_CONST', 100, 'c')

stack.name_op('LOAD_NAME', 101, 'n')
stack.def_op('BUILD_TUPLE', 102, 'I')
stack.def_op('BUILD_LIST', 103, 'I')
stack.def_op('BUILD_SET', 104, 'I')
stack.def_op('BUILD_MAP', 105, 'I')
stack.name_op('LOAD_ATTR', 106, 'n')
stack.def_op('COMPARE_OP', 107, '<')

stack.name_op('IMPORT_NAME', 108, 'n')
stack.name_op('IMPORT_FROM', 109, 'n')

stack.jrel_op('JUMP_FORWARD', 110, 'a')
stack.jabs_op('JUMP_IF_FALSE_OR_POP', 111, 'A')
stack.jabs_op('JUMP_IF_TRUE_OR_POP', 112, 'A')
stack.jabs_op('JUMP_ABSOLUTE', 113, 'A')
stack.jabs_op('POP_JUMP_IF_FALSE', 114, 'A')
stack.jabs_op('POP_JUMP_IF_TRUE', 115, 'A')

stack.name_op('LOAD_GLOBAL', 116, 'n')

stack.def_op('IS_OP', 117, '?')
stack.def_op('CONTAINS_OP', 118, '?')

stack.def_op('JUMP_IF_NOT_EXC_MATCH', 121, 'a')
stack.def_op('SETUP_FINALLY', 122, 'a')

stack.def_op('LOAD_FAST', 124, 'r')

stack.def_op('STORE_FAST', 125, 'r')

stack.def_op('DELETE_FAST', 126, 'r')


stack.def_op('RAISE_VARARGS', 130, 'I')
stack.def_op('CALL_FUNCTION', 131, 'I')
stack.def_op('MAKE_FUNCTION', 132, 'I')
stack.def_op('BUILD_SLICE', 133, 'I')
stack.def_op('LOAD_CLOSURE', 135, '?')

stack.def_op('LOAD_DEREF', 136, '?')

stack.def_op('STORE_DEREF', 137, '?')

stack.def_op('DELETE_DEREF', 138, '?')


stack.def_op('CALL_FUNCTION_KW', 141, '?')
stack.def_op('CALL_FUNCTION_EX', 142, '?')

stack.jrel_op('SETUP_WITH', 143, '?')

stack.def_op('LIST_APPEND', 145, '?')
stack.def_op('SET_ADD', 146, '?')
stack.def_op('MAP_ADD', 147, '?')

stack.def_op('LOAD_CLASSDEREF', 148, '?')


stack.def_op('EXTENDED_ARG', 144, 'n')


stack.jrel_op('SETUP_ASYNC_WITH', 154, '?')

stack.def_op('FORMAT_VALUE', 155, '?')
stack.def_op('BUILD_CONST_KEY_MAP', 156, '?')
stack.def_op('BUILD_STRING', 157, '?')

stack.name_op('LOAD_METHOD', 160, '?')
stack.def_op('CALL_METHOD', 161, '?')

stack.def_op('LIST_EXTEND', 162, '?')
stack.def_op('SET_UPDATE', 163, '?')
stack.def_op('DICT_MERGE', 164, '?')
stack.def_op('DICT_UPDATE', 165, '?')

register = RegisterInstructionSet()

register.def_op('NEW_VM_REG', 0, '000')
register.def_op('BINARY_MATRIX_MULTIPLY_REG', 16, 'rrr')
register.def_op('INPLACE_MATRIX_MULTIPLY_REG', 17, 'rrr')
register.def_op('BINARY_POWER_REG', 19, 'rrr')
register.def_op('BINARY_MULTIPLY_REG', 20, 'rrr')
register.def_op('BINARY_MODULO_REG', 22, 'rrr')
register.def_op('BINARY_ADD_REG', 23, 'rrr')
register.def_op('BINARY_SUBTRACT_REG', 24, 'rrr')
register.def_op('BINARY_SUBSCR_REG', 25, 'rrr')
register.def_op('BINARY_FLOOR_DIVIDE_REG', 26, 'rrr')
register.def_op('BINARY_TRUE_DIVIDE', 27, 'rrr')
register.def_op('RETURN_VALUE_REG', 83, 'r00')
register.def_op('LOAD_CONST_REG', 100, 'rc0')
# TBD... Rattlesnake had four args. I'm trying not to overflow into
# another quad word. If I give this opcode a value <= 64 I have room for
register.def_op('COMPARE_OP_REG', 107, '<rr')
register.jabs_op('POP_JUMP_IF_FALSE_REG', 114, 'A00')
register.jabs_op('POP_JUMP_IF_TRUE_REG', 115, 'A00')
register.def_op('LOAD_FAST_REG', 124, 'rr0')
register.def_op('STORE_FAST_REG', 125, 'rr0')
