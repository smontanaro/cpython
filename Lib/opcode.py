
"""
opcode module - potentially shared between dis and other modules which
operate on bytecodes (e.g. peephole optimizers).
"""

__all__ = ["cmp_op", "hasconst", "hasname", "hasjrel", "hasjabs",
           "haslocal", "hascompare", "hasfree", "opname", "opmap",
           "HAVE_ARGUMENT", "EXTENDED_ARG", "hasnargs", "HAVE_REGISTERS",
           "hasregs", "hasregds", "hasregdss", "hasregdn", "hasregdc",
           "hasregjc", "hasregns",]

# It's a chicken-and-egg I'm afraid:
# We're imported before _opcode's made.
# With exception unheeded
# (stack_effect is not needed)
# Both our chickens and eggs are allayed.
#     --Larry Hastings, 2013/11/23

# Note on messing with the instruction set...
#
# If you modify the instruction set in any way, you will need to do
# the following:
#
# 1. make regen-all
#
# 2. find . -name __pycache__ | xargs rm -r # (or words to that effect)
#
# 3. rebuild the frozen __hello__ module in Python/frozen.c. This worked
#    for me (from the top-level directory):
#
#    a. python3 Tools/freeze/freeze.py -p . Tools/freeze/flag.py
#
#    b. Pluck the frozen module from M___main___.c and use it to replace
#       the guts of the M___hello___ array in Python/frozen.c.
#
#    c. rm M_*.c config.c frozen.c # (or words to that effect)
#
#    d. Rerun configure to regenerate Makefile (which freeze.py overwrote).
#
# 4. Manually regenerate the expected expected_opinfo_* lists in
#    Lib/test/test_dis.py.
#
# There is probably a cleaner way to regenerate M___main___ which wouldn't
# require 3d. I stopped looking for a better solution after I got a usable
# M___hello___ array.
#
# -- Skip 2020-02-29

try:
    from _opcode import stack_effect
    __all__.append('stack_effect')
except ImportError:
    pass

cmp_op = ('<', '<=', '==', '!=', '>', '>=')

hasconst = []
hasname = []
hasjrel = []
hasjabs = []
haslocal = []
hascompare = []
hasfree = []
hasnargs = [] # unused
hasregs = []
hasregds = []
hasregdss = []
hasregdn = []
hasregns = []
hasregdc = []
hasregjc = []

opmap = {}
opname = ['<%r>' % (op,) for op in range(256)]

def def_op(name, op):
    opname[op] = name
    opmap[name] = op

def name_op(name, op):
    def_op(name, op)
    hasname.append(op)

def jrel_op(name, op):
    def_op(name, op)
    hasjrel.append(op)

def jabs_op(name, op):
    def_op(name, op)
    hasjabs.append(op)

# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

op = 0

def_op('POP_TOP', op) ; op += 1
def_op('ROT_TWO', op) ; op += 1
def_op('ROT_THREE', op) ; op += 1
def_op('DUP_TOP', op) ; op += 1
def_op('DUP_TOP_TWO', op) ; op += 1
def_op('ROT_FOUR', op) ; op += 1
def_op('NOP', op) ; op += 1
def_op('UNARY_POSITIVE', op) ; op += 1
def_op('UNARY_NEGATIVE', op) ; op += 1
def_op('UNARY_NOT', op) ; op += 1
def_op('UNARY_INVERT', op) ; op += 1
def_op('BINARY_MATRIX_MULTIPLY', op) ; op += 1
def_op('INPLACE_MATRIX_MULTIPLY', op) ; op += 1
def_op('BINARY_POWER', op) ; op += 1
def_op('BINARY_MULTIPLY', op) ; op += 1
def_op('BINARY_MODULO', op) ; op += 1
def_op('BINARY_ADD', op) ; op += 1
def_op('BINARY_SUBTRACT', op) ; op += 1
def_op('BINARY_SUBSCR', op) ; op += 1
def_op('BINARY_FLOOR_DIVIDE', op) ; op += 1
def_op('BINARY_TRUE_DIVIDE', op) ; op += 1
def_op('INPLACE_FLOOR_DIVIDE', op) ; op += 1
def_op('INPLACE_TRUE_DIVIDE', op) ; op += 1
def_op('RERAISE', op) ; op += 1
def_op('WITH_EXCEPT_START', op) ; op += 1
def_op('GET_AITER', op) ; op += 1
def_op('GET_ANEXT', op) ; op += 1
def_op('BEFORE_ASYNC_WITH', op) ; op += 1
def_op('END_ASYNC_FOR', op) ; op += 1
def_op('INPLACE_ADD', op) ; op += 1
def_op('INPLACE_SUBTRACT', op) ; op += 1
def_op('INPLACE_MULTIPLY', op) ; op += 1
def_op('INPLACE_MODULO', op) ; op += 1
def_op('STORE_SUBSCR', op) ; op += 1
def_op('DELETE_SUBSCR', op) ; op += 1
def_op('BINARY_LSHIFT', op) ; op += 1
def_op('BINARY_RSHIFT', op) ; op += 1
def_op('BINARY_AND', op) ; op += 1
def_op('BINARY_XOR', op) ; op += 1
def_op('BINARY_OR', op) ; op += 1
def_op('INPLACE_POWER', op) ; op += 1
def_op('GET_ITER', op) ; op += 1
def_op('GET_YIELD_FROM_ITER', op) ; op += 1
def_op('PRINT_EXPR', op) ; op += 1
def_op('LOAD_BUILD_CLASS', op) ; op += 1
def_op('YIELD_FROM', op) ; op += 1
def_op('GET_AWAITABLE', op) ; op += 1
def_op('LOAD_ASSERTION_ERROR', op) ; op += 1
def_op('INPLACE_LSHIFT', op) ; op += 1
def_op('INPLACE_RSHIFT', op) ; op += 1
def_op('INPLACE_AND', op) ; op += 1
def_op('INPLACE_XOR', op) ; op += 1
def_op('INPLACE_OR', op) ; op += 1
def_op('LIST_TO_TUPLE', op) ; op += 1
def_op('RETURN_VALUE', op) ; op += 1
def_op('IMPORT_STAR', op) ; op += 1
def_op('SETUP_ANNOTATIONS', op) ; op += 1
def_op('YIELD_VALUE', op) ; op += 1
def_op('POP_BLOCK', op) ; op += 1
def_op('POP_EXCEPT', op) ; op += 1

HAVE_ARGUMENT = op              # Opcodes from here have an argument:

name_op('STORE_NAME', op) ; op += 1       # Index in name list
name_op('DELETE_NAME', op) ; op += 1      # ""
def_op('UNPACK_SEQUENCE', op) ; op += 1   # Number of tuple items
jrel_op('FOR_ITER', op) ; op += 1
def_op('UNPACK_EX', op) ; op += 1
name_op('STORE_ATTR', op) ; op += 1       # Index in name list
name_op('DELETE_ATTR', op) ; op += 1      # ""
name_op('STORE_GLOBAL', op) ; op += 1     # ""
name_op('DELETE_GLOBAL', op) ; op += 1    # ""
hasconst.append(op)
def_op('LOAD_CONST', op) ; op += 1       # Index in const list
name_op('LOAD_NAME', op) ; op += 1       # Index in name list
def_op('BUILD_TUPLE', op) ; op += 1      # Number of tuple items
def_op('BUILD_LIST', op) ; op += 1       # Number of list items
def_op('BUILD_SET', op) ; op += 1        # Number of set items
def_op('BUILD_MAP', op) ; op += 1        # Number of dict entries
name_op('LOAD_ATTR', op) ; op += 1       # Index in name list
hascompare.append(op)
def_op('COMPARE_OP', op) ; op += 1       # Comparison operator
name_op('IMPORT_NAME', op) ; op += 1     # Index in name list
name_op('IMPORT_FROM', op) ; op += 1     # Index in name list
jrel_op('JUMP_FORWARD', op) ; op += 1    # Number of bytes to skip
jabs_op('JUMP_IF_FALSE_OR_POP', op) ; op += 1 # Target byte offset from beginning of code
jabs_op('JUMP_IF_TRUE_OR_POP', op) ; op += 1  # ""
jabs_op('JUMP_ABSOLUTE', op) ; op += 1        # ""
jabs_op('POP_JUMP_IF_FALSE', op) ; op += 1    # ""
jabs_op('POP_JUMP_IF_TRUE', op) ; op += 1     # ""
name_op('LOAD_GLOBAL', op) ; op += 1     # Index in name list
def_op('IS_OP', op) ; op += 1
def_op('CONTAINS_OP', op) ; op += 1
jabs_op('JUMP_IF_NOT_EXC_MATCH', op) ; op += 1
jrel_op('SETUP_FINALLY', op) ; op += 1   # Distance to target address
haslocal.append(op)
def_op('LOAD_FAST', op) ; op += 1        # Local variable number
haslocal.append(op)
def_op('STORE_FAST', op) ; op += 1       # Local variable number
haslocal.append(op)
def_op('DELETE_FAST', op) ; op += 1      # Local variable number

def_op('RAISE_VARARGS', op) ; op += 1    # Number of raise arguments (1, 2, or 3)
def_op('CALL_FUNCTION', op) ; op += 1    # #args
def_op('MAKE_FUNCTION', op) ; op += 1    # Flags
def_op('BUILD_SLICE', op) ; op += 1      # Number of items
hasfree.append(op)
def_op('LOAD_CLOSURE', op) ; op += 1
hasfree.append(op)
def_op('LOAD_DEREF', op) ; op += 1
hasfree.append(op)
def_op('STORE_DEREF', op) ; op += 1
hasfree.append(op)
def_op('DELETE_DEREF', op) ; op += 1
def_op('CALL_FUNCTION_KW', op) ; op += 1  # #args + #kwargs
def_op('CALL_FUNCTION_EX', op) ; op += 1  # Flags
jrel_op('SETUP_WITH', op) ; op += 1
EXTENDED_ARG = op
def_op('EXTENDED_ARG', op) ; op += 1
def_op('LIST_APPEND', op) ; op += 1
def_op('SET_ADD', op) ; op += 1
def_op('MAP_ADD', op) ; op += 1
hasfree.append(op)
def_op('LOAD_CLASSDEREF', op) ; op += 1
jrel_op('SETUP_ASYNC_WITH', op) ; op += 1
def_op('FORMAT_VALUE', op) ; op += 1
def_op('BUILD_CONST_KEY_MAP', op) ; op += 1
def_op('BUILD_STRING', op) ; op += 1
name_op('LOAD_METHOD', op) ; op += 1
def_op('CALL_METHOD', op) ; op += 1
def_op('LIST_EXTEND', op) ; op += 1
def_op('SET_UPDATE', op) ; op += 1
def_op('DICT_MERGE', op) ; op += 1
# Note that Tools/scripts/ generate_opcode_h.py assumes that
# DICT_UPDATE is the last non-register instruction and will need to be
# modified if new instructions are added above.
def_op('DICT_UPDATE', op) ; op += 1

# All register instructions are after here (until we run out of space
# and have to get more crafty).

HAVE_REGISTERS = op

hasregdss.append(op)
def_op('BINARY_ADD_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_AND_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_FLOOR_DIVIDE_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_LSHIFT_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_MATRIX_MULTIPLY_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_MODULO_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_MULTIPLY_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_OR_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_POWER_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_RSHIFT_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_SUBSCR_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_SUBTRACT_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_TRUE_DIVIDE_REG', op) ; op += 1
hasregdss.append(op)
def_op('BINARY_XOR_REG', op) ; op += 1
hasregs.append(op)
def_op('RETURN_VALUE_REG', op) ; op += 1
hasregdc.append(op)
def_op('LOAD_CONST_REG', op) ; op += 1
hasregdn.append(op)
def_op('LOAD_GLOBAL_REG', op) ; op += 1
hasregds.append(op)
def_op('LOAD_FAST_REG', op) ; op += 1
hasregds.append(op)
def_op('STORE_FAST_REG', op) ; op += 1
hasregns.append(op)
def_op('STORE_GLOBAL_REG', op) ; op += 1
hascompare.append(op)
def_op('COMPARE_OP_REG', op) ; op += 1
hasregjc.append(op)
def_op('JUMP_IF_FALSE_REG', op) ; op += 1
hasregjc.append(op)
def_op('JUMP_IF_TRUE_REG', op) ; op += 1
def_op('UNARY_INVERT_REG', op) ; op += 1
def_op('UNARY_NEGATIVE_REG', op) ; op += 1
def_op('UNARY_NOT_REG', op) ; op += 1
def_op('UNARY_POSITIVE_REG', op) ; op += 1
def_op('BUILD_TUPLE_REG', op) ; op += 1
def_op('BUILD_MAP_REG', op) ; op += 1
def_op('BUILD_LIST_REG', op) ; op += 1
def_op('LIST_EXTEND_REG', op) ; op += 1
def_op('CALL_FUNCTION_REG', op) ; op += 1
def_op('CALL_FUNCTION_KW_REG', op) ; op += 1
def_op('INPLACE_ADD_REG', op) ; op += 1
def_op('INPLACE_AND_REG', op) ; op += 1
def_op('INPLACE_FLOOR_DIVIDE_REG', op) ; op += 1
def_op('INPLACE_LSHIFT_REG', op) ; op += 1
def_op('INPLACE_MATRIX_MULTIPLY_REG', op) ; op += 1
def_op('INPLACE_MODULO_REG', op) ; op += 1
def_op('INPLACE_MULTIPLY_REG', op) ; op += 1
def_op('INPLACE_OR_REG', op) ; op += 1
def_op('INPLACE_POWER_REG', op) ; op += 1
def_op('INPLACE_RSHIFT_REG', op) ; op += 1
def_op('INPLACE_SUBTRACT_REG', op) ; op += 1
def_op('INPLACE_TRUE_DIVIDE_REG', op) ; op += 1
def_op('INPLACE_XOR_REG', op) ; op += 1
def_op('LOAD_ATTR_REG', op) ; op += 1
def_op('STORE_ATTR_REG', op) ; op += 1
def_op('DELETE_ATTR_REG', op) ; op += 1
def_op('GET_ITER_REG', op) ; op += 1
jrel_op('FOR_ITER_REG', op) ; op += 1
name_op('IMPORT_NAME_REG', op) ; op += 1     # Index in name list
# def_op('YIELD_VALUE_REG', op) ; op += 1

assert op <= 256, op

del def_op, name_op, jrel_op, jabs_op, op
