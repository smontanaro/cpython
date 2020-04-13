
"""opcodes module - shared between dis and optimize"""

import opcode

__all__ = ["InstructionSet", "ISET"]

class InstructionSet:
    "Repository of instruction set details. Should absorb into opcode.py"
    def __init__(self):
        self.opname = [f'<{op}>' for op in range(256)]
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

    def format(self, op):
        return self.argsmap[op]

OP = 0
ISET = InstructionSet()
def_op = ISET.def_op

def_op('POP_TOP', OP, "0") ; OP += 1
def_op('ROT_TWO', OP, "0") ; OP += 1
def_op('ROT_THREE', OP, "0") ; OP += 1
def_op('DUP_TOP', OP, "0") ; OP += 1
def_op('DUP_TOP_TWO', OP, "0") ; OP += 1
def_op('ROT_FOUR', OP, "0") ; OP += 1
def_op('NOP', OP, "0") ; OP += 1
def_op('UNARY_POSITIVE', OP, "0") ; OP += 1
def_op('UNARY_NEGATIVE', OP, "0") ; OP += 1
def_op('UNARY_NOT', OP, "0") ; OP += 1
def_op('UNARY_INVERT', OP, "0") ; OP += 1
def_op('BINARY_MATRIX_MULTIPLY', OP, "0") ; OP += 1
def_op('INPLACE_MATRIX_MULTIPLY', OP, "0") ; OP += 1
def_op('BINARY_POWER', OP, "0") ; OP += 1
def_op('BINARY_MULTIPLY', OP, "0") ; OP += 1
def_op('BINARY_MODULO', OP, "0") ; OP += 1
def_op('BINARY_ADD', OP, "0") ; OP += 1
def_op('BINARY_SUBTRACT', OP, "0") ; OP += 1
def_op('BINARY_SUBSCR', OP, "0") ; OP += 1
def_op('BINARY_FLOOR_DIVIDE', OP, "0") ; OP += 1
def_op('BINARY_TRUE_DIVIDE', OP, "0") ; OP += 1
def_op('INPLACE_FLOOR_DIVIDE', OP, "0") ; OP += 1
def_op('INPLACE_TRUE_DIVIDE', OP, "0") ; OP += 1
def_op('RERAISE', OP, "0") ; OP += 1
def_op('WITH_EXCEPT_START', OP, "0") ; OP += 1
def_op('GET_AITER', OP, "0") ; OP += 1
def_op('GET_ANEXT', OP, "0") ; OP += 1
def_op('BEFORE_ASYNC_WITH', OP, "0") ; OP += 1
def_op('END_ASYNC_FOR', OP, 'a') ; OP += 1
def_op('INPLACE_ADD', OP, "0") ; OP += 1
def_op('INPLACE_SUBTRACT', OP, "0") ; OP += 1
def_op('INPLACE_MULTIPLY', OP, "0") ; OP += 1
def_op('INPLACE_MODULO', OP, "0") ; OP += 1
def_op('STORE_SUBSCR', OP, "0") ; OP += 1
def_op('DELETE_SUBSCR', OP, "0") ; OP += 1
def_op('BINARY_LSHIFT', OP, "0") ; OP += 1
def_op('BINARY_RSHIFT', OP, "0") ; OP += 1
def_op('BINARY_AND', OP, "0") ; OP += 1
def_op('BINARY_XOR', OP, "0") ; OP += 1
def_op('BINARY_OR', OP, "0") ; OP += 1
def_op('INPLACE_POWER', OP, "0") ; OP += 1
def_op('GET_ITER', OP, "0") ; OP += 1
def_op('GET_YIELD_FROM_ITER', OP, "0") ; OP += 1
def_op('PRINT_EXPR', OP, "0") ; OP += 1
def_op('LOAD_BUILD_CLASS', OP, "0") ; OP += 1
def_op('YIELD_FROM', OP, "0") ; OP += 1
def_op('GET_AWAITABLE', OP, "0") ; OP += 1
def_op('LOAD_ASSERTION_ERROR', OP, "0") ; OP += 1
def_op('INPLACE_LSHIFT', OP, "0") ; OP += 1
def_op('INPLACE_RSHIFT', OP, "0") ; OP += 1
def_op('INPLACE_AND', OP, "0") ; OP += 1
def_op('INPLACE_XOR', OP, "0") ; OP += 1
def_op('INPLACE_OR', OP, "0") ; OP += 1
def_op('LIST_TO_TUPLE', OP, "0") ; OP += 1
def_op('RETURN_VALUE', OP, "0") ; OP += 1
def_op('IMPORT_STAR', OP, "0") ; OP += 1
def_op('SETUP_ANNOTATIONS', OP, "0") ; OP += 1
def_op('YIELD_VALUE', OP, "0") ; OP += 1
def_op('POP_BLOCK', OP, "0") ; OP += 1
def_op('POP_EXCEPT', OP, "0") ; OP += 1

# Opcodes from here have an argument

def_op('STORE_NAME', OP, 'n') ; OP += 1
def_op('DELETE_NAME', OP, 'n') ; OP += 1
def_op('UNPACK_SEQUENCE', OP, 'I') ; OP += 1
def_op('FOR_ITER', OP, 'a') ; OP += 1
def_op('UNPACK_EX', OP, '?') ; OP += 1
def_op('STORE_ATTR', OP, 'n') ; OP += 1
def_op('DELETE_ATTR', OP, 'n') ; OP += 1
def_op('STORE_GLOBAL', OP, 'n') ; OP += 1
def_op('DELETE_GLOBAL', OP, 'n') ; OP += 1

def_op('LOAD_CONST', OP, 'c') ; OP += 1
def_op('LOAD_NAME', OP, 'n') ; OP += 1
def_op('BUILD_TUPLE', OP, 'I') ; OP += 1
def_op('BUILD_LIST', OP, 'I') ; OP += 1
def_op('BUILD_SET', OP, 'I') ; OP += 1
def_op('BUILD_MAP', OP, 'I') ; OP += 1
def_op('LOAD_ATTR', OP, 'n') ; OP += 1

def_op('COMPARE_OP', OP, '<') ; OP += 1
def_op('IMPORT_NAME', OP, 'n') ; OP += 1
def_op('IMPORT_FROM', OP, 'n') ; OP += 1
def_op('JUMP_FORWARD', OP, 'a') ; OP += 1
def_op('JUMP_IF_FALSE_OR_POP', OP, 'A') ; OP += 1
def_op('JUMP_IF_TRUE_OR_POP', OP, 'A') ; OP += 1
def_op('JUMP_ABSOLUTE', OP, 'A') ; OP += 1
def_op('POP_JUMP_IF_FALSE', OP, 'A') ; OP += 1
def_op('POP_JUMP_IF_TRUE', OP, 'A') ; OP += 1
def_op('LOAD_GLOBAL', OP, 'n') ; OP += 1
def_op('IS_OP', OP, '?') ; OP += 1
def_op('CONTAINS_OP', OP, '?') ; OP += 1
def_op('JUMP_IF_NOT_EXC_MATCH', OP, 'a') ; OP += 1
def_op('SETUP_FINALLY', OP, 'a') ; OP += 1

def_op('LOAD_FAST', OP, 'r') ; OP += 1

def_op('STORE_FAST', OP, 'r') ; OP += 1

def_op('DELETE_FAST', OP, 'r') ; OP += 1

def_op('RAISE_VARARGS', OP, 'I') ; OP += 1
def_op('CALL_FUNCTION', OP, 'I') ; OP += 1
def_op('MAKE_FUNCTION', OP, 'I') ; OP += 1
def_op('BUILD_SLICE', OP, 'I') ; OP += 1

def_op('LOAD_CLOSURE', OP, '?') ; OP += 1

def_op('LOAD_DEREF', OP, '?') ; OP += 1

def_op('STORE_DEREF', OP, '?') ; OP += 1

def_op('DELETE_DEREF', OP, '?') ; OP += 1
def_op('CALL_FUNCTION_KW', OP, '?') ; OP += 1
def_op('CALL_FUNCTION_EX', OP, '?') ; OP += 1
def_op('SETUP_WITH', OP, '?') ; OP += 1
def_op('LIST_APPEND', OP, '?') ; OP += 1
def_op('SET_ADD', OP, '?') ; OP += 1
def_op('MAP_ADD', OP, '?') ; OP += 1

def_op('LOAD_CLASSDEREF', OP, '?') ; OP += 1

def_op('EXTENDED_ARG', OP, 'n') ; OP += 1
def_op('SETUP_ASYNC_WITH', OP, '?') ; OP += 1
def_op('FORMAT_VALUE', OP, '?') ; OP += 1
def_op('BUILD_CONST_KEY_MAP', OP, '?') ; OP += 1
def_op('BUILD_STRING', OP, '?') ; OP += 1
def_op('LOAD_METHOD', OP, '?') ; OP += 1
def_op('CALL_METHOD', OP, '?') ; OP += 1
def_op('LIST_EXTEND', OP, '?') ; OP += 1
def_op('SET_UPDATE', OP, '?') ; OP += 1
def_op('DICT_MERGE', OP, '?') ; OP += 1
def_op('DICT_UPDATE', OP, '?') ; OP += 1

def_op('BINARY_POWER_REG', OP, 'rrr') ; OP += 1
def_op('BINARY_MULTIPLY_REG', OP, 'rrr') ; OP += 1
def_op('BINARY_MODULO_REG', OP, 'rrr') ; OP += 1
def_op('BINARY_ADD_REG', OP, 'rrr') ; OP += 1
def_op('BINARY_SUBTRACT_REG', OP, 'rrr') ; OP += 1
def_op('BINARY_SUBSCR_REG', OP, 'rrr') ; OP += 1
def_op('BINARY_FLOOR_DIVIDE_REG', OP, 'rrr') ; OP += 1
def_op('BINARY_TRUE_DIVIDE_REG', OP, 'rrr') ; OP += 1
def_op('RETURN_VALUE_REG', OP, 'r00') ; OP += 1
def_op('LOAD_CONST_REG', OP, 'rc0') ; OP += 1
def_op('LOAD_GLOBAL_REG', OP, 'nr0') ; OP += 1
def_op('LOAD_FAST_REG', OP, 'rr0') ; OP += 1
def_op('STORE_FAST_REG', OP, 'rr0') ; OP += 1
def_op('COMPARE_OP_REG', OP, '<rr') ; OP += 1
def_op('JUMP_IF_FALSE_REG', OP, 'A') ; OP += 1
def_op('JUMP_IF_TRUE_REG', OP, 'A') ; OP += 1
def_op('UNARY_NOT_REG', OP, 'rr') ; OP += 1
def_op('BUILD_TUPLE_REG', OP, 'rrr') ; OP += 1
def_op('BUILD_LIST_REG', OP, 'rrr') ; OP += 1
def_op('LIST_EXTEND_REG', OP, 'rrr') ; OP += 1
def_op('CALL_FUNCTION_REG', OP, 'rrN') ; OP += 1

assert OP <= 256, OP

del def_op, OP
