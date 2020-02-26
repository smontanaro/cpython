
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

    def def_op(self, name, op, argfmt=""):
        """Associate an opcode with a name & describe arguments.

        Argfmt serves two purposes.  Its length tells how many argument
        bytes the opcode has, and its contents interpret each byte's
        functionality.  The different characters in an argfmt mean:

        + - second byte of a two-byte argument
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
    def has_argument(self, op):
        return op & 3

    def def_op(self, name, op, argfmt=""):
        """Associate an opcode with a name & describe arguments.

        Argfmt indicates how many arg bytes the instruction takes. We
        only allow two bits for that segment of the opcode, so instructions
        that use more than three bytes are handled specially in ceval.c.

        See base class for further description of argfmt.
        """
        argn = min(3, len(argfmt))
        opcode = (op<<2) | argn
        self.opmap[name] = opcode
        self.opname[opcode] = name
        self.argsmap[opcode] = argfmt
        #print "defop", (name, op, argfmt, oct(opcode), opcode, `chr(opcode)`)


stack = StackInstructionSet()
#               name                    opcode          args
stack.def_op('POP_TOP', 1, '')
stack.def_op('ROT_TWO', 2, '')
stack.def_op('ROT_THREE', 3, '')
stack.def_op('DUP_TOP', 4, '')
stack.def_op('DUP_TOP_TWO', 5, '')
stack.def_op('ROT_FOUR', 6, '')

stack.def_op('NOP', 9, '')
stack.def_op('UNARY_POSITIVE', 10, '')
stack.def_op('UNARY_NEGATIVE', 11, '')
stack.def_op('UNARY_NOT', 12, '')

stack.def_op('UNARY_INVERT', 15, '')

stack.def_op('BINARY_MATRIX_MULTIPLY', 16, '')
stack.def_op('INPLACE_MATRIX_MULTIPLY', 16, '')

stack.def_op('BINARY_POWER', 19, '')
stack.def_op('BINARY_MULTIPLY', 20, '')

stack.def_op('BINARY_MODULO', 22, '')
stack.def_op('BINARY_ADD', 23, '')
stack.def_op('BINARY_SUBTRACT', 24, '')
stack.def_op('BINARY_SUBSCR', 25, '')
stack.def_op('BINARY_FLOOR_DIVIDE', 26, '')
stack.def_op('BINARY_TRUE_DIVIDE', 27, '')
stack.def_op('INPLACE_FLOOR_DIVIDE', 28, '')
stack.def_op('INPLACE_TRUE_DIVIDE', 29, '')

stack.def_op('RERAISE', 48, '')
stack.def_op('WITH_EXCEPT_START', 49, '')
stack.def_op('GET_AITER', 50, '')
stack.def_op('GET_ANEXT', 51, '')
stack.def_op('BEFORE_ASYNC_WITH', 52, '')

stack.def_op('END_ASYNC_FOR', 54, '')
stack.def_op('INPLACE_ADD', 55, '')
stack.def_op('INPLACE_SUBTRACT', 56, '')
stack.def_op('INPLACE_MULTIPLY', 57, '')

stack.def_op('INPLACE_MODULO', 59, '')
stack.def_op('STORE_SUBSCR', 60, '')
stack.def_op('DELETE_SUBSCR', 61, '')
stack.def_op('BINARY_LSHIFT', 62, '')
stack.def_op('BINARY_RSHIFT', 63, '')
stack.def_op('BINARY_AND', 64, '')
stack.def_op('BINARY_XOR', 65, '')
stack.def_op('BINARY_OR', 66, '')
stack.def_op('INPLACE_POWER', 67, '')
stack.def_op('GET_ITER', 68, '')
stack.def_op('GET_YIELD_FROM_ITER', 69, '')

stack.def_op('PRINT_EXPR', 70, '')
stack.def_op('LOAD_BUILD_CLASS', 71, '')
stack.def_op('YIELD_FROM', 72, '')
stack.def_op('GET_AWAITABLE', 73, '')
stack.def_op('LOAD_ASSERTION_ERROR', 74, '')
stack.def_op('INPLACE_LSHIFT', 75, '')
stack.def_op('INPLACE_RSHIFT', 76, '')
stack.def_op('INPLACE_AND', 77, '')
stack.def_op('INPLACE_XOR', 78, '')
stack.def_op('INPLACE_OR', 79, '')

stack.def_op('LIST_TO_TUPLE', 82, '')
stack.def_op('RETURN_VALUE', 83, '')
stack.def_op('IMPORT_STAR', 84, '')
stack.def_op('SETUP_ANNOTATIONS', 85, '')
stack.def_op('YIELD_VALUE', 86, '')
stack.def_op('POP_BLOCK', 87, '')

stack.def_op('POP_EXCEPT', 89, '')

# Opcodes from here have an argument

stack.name_op('STORE_NAME', 90, 'n+')
stack.name_op('DELETE_NAME', 91, 'n+')
stack.def_op('UNPACK_SEQUENCE', 92, 'I+')
stack.jrel_op('FOR_ITER', 93, '???')
stack.def_op('UNPACK_EX', 94, '???')
stack.name_op('STORE_ATTR', 95, 'n+')
stack.name_op('DELETE_ATTR', 96, 'n+')
stack.name_op('STORE_GLOBAL', 97, 'n+')
stack.name_op('DELETE_GLOBAL', 98, 'n+')
stack.def_op('LOAD_CONST', 100, 'c+')

stack.name_op('LOAD_NAME', 101, 'n+')
stack.def_op('BUILD_TUPLE', 102, 'I+')
stack.def_op('BUILD_LIST', 103, 'I+')
stack.def_op('BUILD_SET', 104, 'I+')
stack.def_op('BUILD_MAP', 105, 'I+')
stack.name_op('LOAD_ATTR', 106, 'n+')
stack.def_op('COMPARE_OP', 107, '<+')

stack.name_op('IMPORT_NAME', 108, 'n+')
stack.name_op('IMPORT_FROM', 109, 'n+')

stack.jrel_op('JUMP_FORWARD', 110, 'a+')
stack.jabs_op('JUMP_IF_FALSE_OR_POP', 111, 'a+')
stack.jabs_op('JUMP_IF_TRUE_OR_POP', 112, 'a+')
stack.jabs_op('JUMP_ABSOLUTE', 113, 'A+')
stack.jabs_op('POP_JUMP_IF_FALSE', 114, '???')
stack.jabs_op('POP_JUMP_IF_TRUE', 115, '???')

stack.name_op('LOAD_GLOBAL', 116, 'n+')

stack.def_op('IS_OP', 117, '???')
stack.def_op('CONTAINS_OP', 118, '???')

stack.def_op('JUMP_IF_NOT_EXC_MATCH', 121, '???')
stack.def_op('SETUP_FINALLY', 122, 'a+')

stack.def_op('LOAD_FAST', 124, 'r+')

stack.def_op('STORE_FAST', 125, 'r+')

stack.def_op('DELETE_FAST', 126, 'r+')


stack.def_op('RAISE_VARARGS', 130, 'I+')
stack.def_op('CALL_FUNCTION', 131, 'II')
stack.def_op('MAKE_FUNCTION', 132, 'I+')
stack.def_op('BUILD_SLICE', 133, 'I+')
stack.def_op('LOAD_CLOSURE', 135, '???')

stack.def_op('LOAD_DEREF', 136, '???')

stack.def_op('STORE_DEREF', 137, '???')

stack.def_op('DELETE_DEREF', 138, '???')


stack.def_op('CALL_FUNCTION_KW', 141, '???')
stack.def_op('CALL_FUNCTION_EX', 142, '???')

stack.jrel_op('SETUP_WITH', 143, '???')

stack.def_op('LIST_APPEND', 145, '???')
stack.def_op('SET_ADD', 146, '???')
stack.def_op('MAP_ADD', 147, '???')

stack.def_op('LOAD_CLASSDEREF', 148, '???')


stack.def_op('EXTENDED_ARG', 144, '???')


stack.jrel_op('SETUP_ASYNC_WITH', 154, '???')

stack.def_op('FORMAT_VALUE', 155, '???')
stack.def_op('BUILD_CONST_KEY_MAP', 156, '???')
stack.def_op('BUILD_STRING', 157, '???')

stack.name_op('LOAD_METHOD', 160, '???')
stack.def_op('CALL_METHOD', 161, '???')

stack.def_op('LIST_EXTEND', 162, '???')
stack.def_op('SET_UPDATE', 163, '???')
stack.def_op('DICT_MERGE', 164, '???')
stack.def_op('DICT_UPDATE', 165, '???')

register = RegisterInstructionSet()

register.def_op('STOP_CODE_REG', 0, '')
register.def_op('BREAK_LOOP_REG', 1, '')
register.def_op('PRINT_NEWLINE_REG', 2, '')
register.def_op('POP_BLOCK_REG', 3, '')
register.def_op('RAISE_0_REG', 22, '')
register.def_op('POP_TOP_REG', 1, 'n')
register.def_op('DELETE_GLOBAL_REG', 3, 'n')
register.def_op('LOAD_NONE_REG', 4, 'r')
register.def_op('ROT_TWO_REG', 5, 'r')
register.def_op('ROT_THREE_REG', 6, 'r')
register.def_op('PRINT_EXPR_REG', 12, 'r')
register.def_op('PRINT_ITEM_REG', 13, 'r')
register.def_op('LOAD_LOCALS_REG', 14, 'r')
register.def_op('RETURN_VALUE_REG', 15, 'r')
register.def_op('BUILD_MAP_REG', 16, 'r')
register.def_op('RAISE_1_REG', 22, 'r')
register.def_op('DELETE_FAST_REG', 35, 'r')
register.def_op('DELETE_SUBSCR_REG', 1, '??')
register.def_op('JUMP_FORWARD_REG', 4, 'a+')
register.def_op('JUMP_ABSOLUTE_REG', 5, 'A+')
register.def_op('UNARY_POSITIVE_REG', 6, 'rr')
register.def_op('UNARY_NEGATIVE_REG', 7, 'rr')
register.def_op('UNARY_NOT_REG', 8, 'rr')
register.def_op('UNARY_CONVERT_REG', 9, 'rr')
register.def_op('UNARY_INVERT_REG', 10, 'rr')
register.def_op('RAISE_2_REG', 22, 'rr')
register.def_op('UNPACK_TUPLE_REG', 24, 'rI')
register.def_op('UNPACK_LIST_REG', 25, 'rI')
register.def_op('LOAD_FAST_REG', 33, 'rr')
register.def_op('STORE_FAST_REG', 34, 'rr')
register.def_op('IMPORT_NAME_REG', 49, 'rn')
register.def_op('LOAD_GLOBAL_REG', 51, 'rn')
register.def_op('DELETE_ATTR_REG', 53, 'rn')
register.def_op('STORE_GLOBAL_REG', 54, 'rn')
register.def_op('LOAD_CONST_REG', 55, 'rc')
register.def_op('LOAD_ATTR_REG', 1, 'rrn')
register.def_op('COMPARE_OP_REG', 2, 'rrr<')
register.def_op('EXEC_STMT_REG', 3, 'rrr')
register.def_op('SETUP_LOOP_REG', 4, 'a+I')
register.def_op('STORE_ATTR_REG', 5, 'rnr')
register.def_op('BINARY_POWER_REG', 11, 'rrr')
register.def_op('BINARY_MULTIPLY_REG', 12, 'rrr')
register.def_op('BINARY_DIVIDE_REG', 13, 'rrr')
register.def_op('BINARY_MODULO_REG', 14, 'rrr')
register.def_op('BINARY_ADD_REG', 15, 'rrr')
register.def_op('BINARY_SUBTRACT_REG', 16, 'rrr')
register.def_op('BINARY_SUBSCR_REG', 17, 'rrr')
register.def_op('BUILD_TUPLE_REG', 18, 'rrI')
register.def_op('BUILD_LIST_REG', 19, 'rrI')
register.def_op('JUMP_IF_FALSE_REG', 20, 'a+r')
register.def_op('JUMP_IF_TRUE_REG', 21, 'a+r')
register.def_op('RAISE_3_REG', 22, 'rrr')
register.def_op('FOR_LOOP_REG', 23, 'a+rrr')
register.def_op('STORE_SUBSCR_REG', 30, '???')
register.def_op('CALL_FUNCTION_REG', 38, 'IIr')
register.def_op('MAKE_FUNCTION_REG', 39, 'rIr')
register.def_op('BUILD_CLASS_REG', 41, 'rrr')
register.def_op('BINARY_LSHIFT_REG', 43, 'rrr')
register.def_op('BINARY_RSHIFT_REG', 44, 'rrr')
register.def_op('BINARY_AND_REG', 45, 'rrr')
register.def_op('BINARY_XOR_REG', 46, 'rrr')
register.def_op('BINARY_OR_REG', 47, 'rrr')
