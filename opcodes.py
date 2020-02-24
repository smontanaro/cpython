
"""opcodes module - shared between dis and optimize"""

# range of small_int cache - values must match with those used by intobject.c
NSMALLPOSINTS = 100
NSMALLNEGINTS = 1

cmp_op = ('<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is',
          'is not', 'exception match', 'BAD')

class InstructionSet:
    def __init__(self):
        self.opname = [''] * 256
        for op in range(256): self.opname[op] = '<' + repr(op) + '>'
        self.opmap = {}
        self.argsmap = {}

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
        bytes = min(3, len(argfmt))
        opcode = (op<<2)|bytes
        self.opmap[name] = opcode
        self.opname[opcode] = name
        self.argsmap[opcode] = argfmt
        #print "defop", (name, op, argfmt, oct(opcode), opcode, `chr(opcode)`)


stack = StackInstructionSet()
#		name			opcode		args
stack.def_op(	'STOP_CODE',	        0,		'')
stack.def_op(	'POP_TOP',		1,		'')
stack.def_op(	'ROT_TWO',		2,		'')
stack.def_op(	'ROT_THREE',	        3,		'')
stack.def_op(	'DUP_TOP',		4,		'')
stack.def_op(	'LOAD_NONE',	        5,		'')
stack.def_op(	'UNARY_POSITIVE',	10,		'')
stack.def_op(	'UNARY_NEGATIVE',	11,		'')
stack.def_op(	'UNARY_NOT',	        12,		'')
stack.def_op(	'UNARY_CONVERT',	13,		'')
stack.def_op(	'UNARY_INVERT',	        15,		'')
stack.def_op(	'BINARY_POWER',	        19,		'')
stack.def_op(	'BINARY_MULTIPLY',	20,		'')
stack.def_op(	'BINARY_DIVIDE',	21,		'')
stack.def_op(	'BINARY_MODULO',	22,		'')
stack.def_op(	'BINARY_ADD',	        23,		'')
stack.def_op(	'BINARY_SUBTRACT',	24,		'')
stack.def_op(	'BINARY_SUBSCR',	25,		'')
stack.def_op(	'SLICE+0',		30,		'')
stack.def_op(	'SLICE+1',		31,		'')
stack.def_op(	'SLICE+2',		32,		'')
stack.def_op(	'SLICE+3',		33,		'')
stack.def_op(	'STORE_SLICE+0',	40,		'')
stack.def_op(	'STORE_SLICE+1',	41,		'')
stack.def_op(	'STORE_SLICE+2',	42,		'')
stack.def_op(	'STORE_SLICE+3',	43,		'')
stack.def_op(	'DELETE_SLICE+0',	50,		'')
stack.def_op(	'DELETE_SLICE+1',	51,		'')
stack.def_op(	'DELETE_SLICE+2',	52,		'')
stack.def_op(	'DELETE_SLICE+3',	53,		'')
stack.def_op(	'STORE_SUBSCR',	        60,		'')
stack.def_op(	'DELETE_SUBSCR',	61,		'')
stack.def_op(	'BINARY_LSHIFT',	62,		'')
stack.def_op(	'BINARY_RSHIFT',	63,		'')
stack.def_op(	'BINARY_AND',	        64,		'')
stack.def_op(	'BINARY_XOR',	        65,		'')
stack.def_op(	'BINARY_OR',	        66,		'')
stack.def_op(	'PRINT_EXPR',	        70,		'')
stack.def_op(	'PRINT_ITEM',	        71,		'')
stack.def_op(	'PRINT_NEWLINE',	72,		'')
stack.def_op(	'BREAK_LOOP',	        80,		'')
stack.def_op(	'LOAD_LOCALS',	        82,		'')
stack.def_op(	'RETURN_VALUE',	        83,		'')
stack.def_op(	'EXEC_STMT',	        85,		'')
stack.def_op(	'POP_BLOCK',	        87,		'')
stack.def_op(	'END_FINALLY',	        88,		'')
stack.def_op(	'BUILD_CLASS',	        89,		'')
stack.def_op(	'STORE_NAME',	        90,		'n+')
stack.def_op(	'DELETE_NAME',	        91,		'n+')
stack.def_op(	'UNPACK_TUPLE',	        92,		'I+')
stack.def_op(	'UNPACK_LIST',	        93,		'I+')
stack.def_op(	'STORE_ATTR',	        95,		'n+')
stack.def_op(	'DELETE_ATTR',	        96,		'n+')
stack.def_op(	'STORE_GLOBAL',	        97,		'n+')
stack.def_op(	'DELETE_GLOBAL',	98,		'n+')
stack.def_op(	'LOAD_CONST',	        100,		'c+')
stack.def_op(	'LOAD_NAME',	        101,		'n+')
stack.def_op(	'BUILD_TUPLE',	        102,		'I+')
stack.def_op(	'BUILD_LIST',	        103,		'I+')
stack.def_op(	'BUILD_MAP',	        104,		'I+')
stack.def_op(	'LOAD_ATTR',	        105,		'n+')
stack.def_op(	'COMPARE_OP',	        106,		'<+')
stack.def_op(	'IMPORT_NAME',	        107,		'n+')
stack.def_op(	'IMPORT_FROM',	        108,		'n+')
stack.def_op(	'JUMP_FORWARD',	        110,		'a+')
stack.def_op(	'JUMP_IF_FALSE',	111,		'a+')
stack.def_op(	'JUMP_IF_TRUE',	        112,		'a+')
stack.def_op(	'JUMP_ABSOLUTE',	113,		'A+')
stack.def_op(	'FOR_LOOP',	        114,		'a+')
stack.def_op(	'LOAD_GLOBAL',	        116,		'n+')
stack.def_op(	'LOAD_ATTR_FAST',	118,		'rn')
stack.def_op(	'STORE_ATTR_FAST',	119,		'rn')
stack.def_op(	'SETUP_LOOP',	        120,		'a+')
stack.def_op(	'SETUP_EXCEPT',	        121,		'a+')
stack.def_op(	'SETUP_FINALLY',	122,		'a+')
stack.def_op(	'LOAD_FAST',	        124,		'r+')
stack.def_op(	'STORE_FAST',	        125,		'r+')
stack.def_op(	'DELETE_FAST',	        126,		'r+')
stack.def_op(	'SET_LINENO',	        127,		'L+')
stack.def_op(	'RAISE_VARARGS',	130,		'I+')
stack.def_op(	'CALL_FUNCTION',	131,		'II')
stack.def_op(	'MAKE_FUNCTION',	132,		'I+')
stack.def_op(	'BUILD_SLICE',	        133,		'I+')

register = RegisterInstructionSet()

register.def_op('STOP_CODE_REG',	0,		'')
register.def_op('BREAK_LOOP_REG',	1,		'')
register.def_op('PRINT_NEWLINE_REG',	2,		'')
register.def_op('POP_BLOCK_REG',	3,		'')
register.def_op('RAISE_0_REG',		22,		'')
register.def_op('POP_TOP_REG',		1,		'n')
register.def_op('DELETE_GLOBAL_REG',	3,		'n')
register.def_op('LOAD_NONE_REG',	4,		'r')
register.def_op('ROT_TWO_REG',		5,		'r')
register.def_op('ROT_THREE_REG',	6,		'r')
register.def_op('PRINT_EXPR_REG',	12,		'r')
register.def_op('PRINT_ITEM_REG',	13,		'r')
register.def_op('LOAD_LOCALS_REG',	14,		'r')
register.def_op('RETURN_VALUE_REG',	15,		'r')
register.def_op('BUILD_MAP_REG',	16,		'r')
register.def_op('RAISE_1_REG',		22,		'r')
register.def_op('DELETE_FAST_REG',	35,		'r')
register.def_op('DELETE_SUBSCR_REG',	1,		'??')
register.def_op('JUMP_FORWARD_REG',	4,		'a+')
register.def_op('JUMP_ABSOLUTE_REG',	5,		'A+')
register.def_op('UNARY_POSITIVE_REG',	6,		'rr')
register.def_op('UNARY_NEGATIVE_REG',	7,		'rr')
register.def_op('UNARY_NOT_REG',	8,		'rr')
register.def_op('UNARY_CONVERT_REG',	9,		'rr')
register.def_op('UNARY_INVERT_REG',	10,		'rr')
register.def_op('RAISE_2_REG',		22,		'rr')
register.def_op('UNPACK_TUPLE_REG',	24,		'rI')
register.def_op('UNPACK_LIST_REG',	25,		'rI')
register.def_op('LOAD_FAST_REG',	33,		'rr')
register.def_op('STORE_FAST_REG',	34,		'rr')
register.def_op('IMPORT_NAME_REG',	49,		'rn')
register.def_op('LOAD_GLOBAL_REG',	51,		'rn')
register.def_op('DELETE_ATTR_REG',	53,		'rn')
register.def_op('STORE_GLOBAL_REG',	54,		'rn')
register.def_op('LOAD_CONST_REG',	55,		'rc')
register.def_op('LOAD_ATTR_REG',	1,		'rrn')
register.def_op('COMPARE_OP_REG',	2,		'rrr<')
register.def_op('EXEC_STMT_REG',	3,		'rrr')
register.def_op('SETUP_LOOP_REG',	4,		'a+I')
register.def_op('STORE_ATTR_REG',	5,		'rnr')
register.def_op('BINARY_POWER_REG',	11,		'rrr')
register.def_op('BINARY_MULTIPLY_REG',	12,		'rrr')
register.def_op('BINARY_DIVIDE_REG',	13,		'rrr')
register.def_op('BINARY_MODULO_REG',	14,		'rrr')
register.def_op('BINARY_ADD_REG',	15,		'rrr')
register.def_op('BINARY_SUBTRACT_REG',	16,		'rrr')
register.def_op('BINARY_SUBSCR_REG',	17,		'rrr')
register.def_op('BUILD_TUPLE_REG',	18,		'rrI')
register.def_op('BUILD_LIST_REG',	19,		'rrI')
register.def_op('JUMP_IF_FALSE_REG',	20,		'a+r')
register.def_op('JUMP_IF_TRUE_REG',	21,		'a+r')
register.def_op('RAISE_3_REG',		22,		'rrr')
register.def_op('FOR_LOOP_REG',		23,		'a+rrr')
register.def_op('STORE_SUBSCR_REG',	30,		'???')
register.def_op('CALL_FUNCTION_REG',	38,		'IIr')
register.def_op('MAKE_FUNCTION_REG',	39,		'rIr')
register.def_op('BUILD_CLASS_REG',	41,		'rrr')
register.def_op('BINARY_LSHIFT_REG',	43,		'rrr')
register.def_op('BINARY_RSHIFT_REG',	44,		'rrr')
register.def_op('BINARY_AND_REG',	45,		'rrr')
register.def_op('BINARY_XOR_REG',	46,		'rrr')
register.def_op('BINARY_OR_REG',	47,		'rrr')
