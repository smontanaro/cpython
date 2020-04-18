/* Auto-generated by Tools/scripts/generate_opcode_h.py from Lib/opcode.py */
#ifndef Py_OPCODE_H
#define Py_OPCODE_H
#ifdef __cplusplus
extern "C" {
#endif


    /* Instruction opcodes for compiled code */
#define POP_TOP                   0
#define ROT_TWO                   1
#define ROT_THREE                 2
#define DUP_TOP                   3
#define DUP_TOP_TWO               4
#define ROT_FOUR                  5
#define NOP                       6
#define UNARY_POSITIVE            7
#define UNARY_NEGATIVE            8
#define UNARY_NOT                 9
#define UNARY_INVERT             10
#define BINARY_MATRIX_MULTIPLY   11
#define INPLACE_MATRIX_MULTIPLY  12
#define BINARY_POWER             13
#define BINARY_MULTIPLY          14
#define BINARY_MODULO            15
#define BINARY_ADD               16
#define BINARY_SUBTRACT          17
#define BINARY_SUBSCR            18
#define BINARY_FLOOR_DIVIDE      19
#define BINARY_TRUE_DIVIDE       20
#define INPLACE_FLOOR_DIVIDE     21
#define INPLACE_TRUE_DIVIDE      22
#define RERAISE                  23
#define WITH_EXCEPT_START        24
#define GET_AITER                25
#define GET_ANEXT                26
#define BEFORE_ASYNC_WITH        27
#define END_ASYNC_FOR            28
#define INPLACE_ADD              29
#define INPLACE_SUBTRACT         30
#define INPLACE_MULTIPLY         31
#define INPLACE_MODULO           32
#define STORE_SUBSCR             33
#define DELETE_SUBSCR            34
#define BINARY_LSHIFT            35
#define BINARY_RSHIFT            36
#define BINARY_AND               37
#define BINARY_XOR               38
#define BINARY_OR                39
#define INPLACE_POWER            40
#define GET_ITER                 41
#define GET_YIELD_FROM_ITER      42
#define PRINT_EXPR               43
#define LOAD_BUILD_CLASS         44
#define YIELD_FROM               45
#define GET_AWAITABLE            46
#define LOAD_ASSERTION_ERROR     47
#define INPLACE_LSHIFT           48
#define INPLACE_RSHIFT           49
#define INPLACE_AND              50
#define INPLACE_XOR              51
#define INPLACE_OR               52
#define LIST_TO_TUPLE            53
#define RETURN_VALUE             54
#define IMPORT_STAR              55
#define SETUP_ANNOTATIONS        56
#define YIELD_VALUE              57
#define POP_BLOCK                58
#define POP_EXCEPT               59
#define HAVE_ARGUMENT            60
#define STORE_NAME               60
#define DELETE_NAME              61
#define UNPACK_SEQUENCE          62
#define FOR_ITER                 63
#define UNPACK_EX                64
#define STORE_ATTR               65
#define DELETE_ATTR              66
#define STORE_GLOBAL             67
#define DELETE_GLOBAL            68
#define LOAD_CONST               69
#define LOAD_NAME                70
#define BUILD_TUPLE              71
#define BUILD_LIST               72
#define BUILD_SET                73
#define BUILD_MAP                74
#define LOAD_ATTR                75
#define COMPARE_OP               76
#define IMPORT_NAME              77
#define IMPORT_FROM              78
#define JUMP_FORWARD             79
#define JUMP_IF_FALSE_OR_POP     80
#define JUMP_IF_TRUE_OR_POP      81
#define JUMP_ABSOLUTE            82
#define POP_JUMP_IF_FALSE        83
#define POP_JUMP_IF_TRUE         84
#define LOAD_GLOBAL              85
#define IS_OP                    86
#define CONTAINS_OP              87
#define JUMP_IF_NOT_EXC_MATCH    88
#define SETUP_FINALLY            89
#define LOAD_FAST                90
#define STORE_FAST               91
#define DELETE_FAST              92
#define RAISE_VARARGS            93
#define CALL_FUNCTION            94
#define MAKE_FUNCTION            95
#define BUILD_SLICE              96
#define LOAD_CLOSURE             97
#define LOAD_DEREF               98
#define STORE_DEREF              99
#define DELETE_DEREF            100
#define CALL_FUNCTION_KW        101
#define CALL_FUNCTION_EX        102
#define SETUP_WITH              103
#define LIST_APPEND             104
#define SET_ADD                 105
#define MAP_ADD                 106
#define LOAD_CLASSDEREF         107
#define EXTENDED_ARG            108
#define SETUP_ASYNC_WITH        109
#define FORMAT_VALUE            110
#define BUILD_CONST_KEY_MAP     111
#define BUILD_STRING            112
#define LOAD_METHOD             113
#define CALL_METHOD             114
#define LIST_EXTEND             115
#define SET_UPDATE              116
#define DICT_MERGE              117
#define DICT_UPDATE             118
#define HAVE_REGISTERS          119
#define BINARY_ADD_REG          119
#define BINARY_AND_REG          120
#define BINARY_FLOOR_DIVIDE_REG 121
#define BINARY_LSHIFT_REG       122
#define BINARY_MATRIX_MULTIPLY_REG 123
#define BINARY_MODULO_REG       124
#define BINARY_MULTIPLY_REG     125
#define BINARY_OR_REG           126
#define BINARY_POWER_REG        127
#define BINARY_RSHIFT_REG       128
#define BINARY_SUBSCR_REG       129
#define BINARY_SUBTRACT_REG     130
#define BINARY_TRUE_DIVIDE_REG  131
#define BINARY_XOR_REG          132
#define RETURN_VALUE_REG        133
#define LOAD_CONST_REG          134
#define LOAD_GLOBAL_REG         135
#define LOAD_FAST_REG           136
#define STORE_FAST_REG          137
#define COMPARE_OP_REG          138
#define JUMP_IF_FALSE_REG       139
#define JUMP_IF_TRUE_REG        140
#define UNARY_INVERT_REG        141
#define UNARY_NEGATIVE_REG      142
#define UNARY_NOT_REG           143
#define UNARY_POSITIVE_REG      144
#define BUILD_TUPLE_REG         145
#define BUILD_MAP_REG           146
#define BUILD_LIST_REG          147
#define LIST_EXTEND_REG         148
#define CALL_FUNCTION_REG       149
#define CALL_FUNCTION_KW_REG    150
#define INPLACE_ADD_REG         151
#define INPLACE_AND_REG         152
#define INPLACE_FLOOR_DIVIDE_REG 153
#define INPLACE_LSHIFT_REG      154
#define INPLACE_MATRIX_MULTIPLY_REG 155
#define INPLACE_MODULO_REG      156
#define INPLACE_MULTIPLY_REG    157
#define INPLACE_OR_REG          158
#define INPLACE_POWER_REG       159
#define INPLACE_RSHIFT_REG      160
#define INPLACE_SUBTRACT_REG    161
#define INPLACE_TRUE_DIVIDE_REG 162
#define INPLACE_XOR_REG         163

/* EXCEPT_HANDLER is a special, implicit block type which is created when
   entering an except handler. It is not an opcode but we define it here
   as we want it to be available to both frameobject.c and ceval.c, while
   remaining private.*/
#define EXCEPT_HANDLER 257

#define HAS_ARG(op) ((op) >= HAVE_ARGUMENT)

#define HAS_REGISTERS(op) ((op) >= HAVE_REGISTERS)

#ifdef __cplusplus
}
#endif
#endif /* !Py_OPCODE_H */
