static char *opcode_map[256] = {
    "POP_TOP",
    "ROT_TWO",
    "ROT_THREE",
    "DUP_TOP",
    "DUP_TOP_TWO",
    "ROT_FOUR",
    "NOP",
    "UNARY_POSITIVE",
    "UNARY_NEGATIVE",
    "UNARY_NOT",
    "UNARY_INVERT",
    "BINARY_MATRIX_MULTIPLY",
    "INPLACE_MATRIX_MULTIPLY",
    "BINARY_POWER",
    "BINARY_MULTIPLY",
    "BINARY_MODULO",
    "BINARY_ADD",
    "BINARY_SUBTRACT",
    "BINARY_SUBSCR",
    "BINARY_FLOOR_DIVIDE",
    "BINARY_TRUE_DIVIDE",
    "INPLACE_FLOOR_DIVIDE",
    "INPLACE_TRUE_DIVIDE",
    "RERAISE",
    "WITH_EXCEPT_START",
    "GET_AITER",
    "GET_ANEXT",
    "BEFORE_ASYNC_WITH",
    "END_ASYNC_FOR",
    "INPLACE_ADD",
    "INPLACE_SUBTRACT",
    "INPLACE_MULTIPLY",
    "INPLACE_MODULO",
    "STORE_SUBSCR",
    "DELETE_SUBSCR",
    "BINARY_LSHIFT",
    "BINARY_RSHIFT",
    "BINARY_AND",
    "BINARY_XOR",
    "BINARY_OR",
    "INPLACE_POWER",
    "GET_ITER",
    "GET_YIELD_FROM_ITER",
    "PRINT_EXPR",
    "LOAD_BUILD_CLASS",
    "YIELD_FROM",
    "GET_AWAITABLE",
    "LOAD_ASSERTION_ERROR",
    "INPLACE_LSHIFT",
    "INPLACE_RSHIFT",
    "INPLACE_AND",
    "INPLACE_XOR",
    "INPLACE_OR",
    "LIST_TO_TUPLE",
    "RETURN_VALUE",
    "IMPORT_STAR",
    "SETUP_ANNOTATIONS",
    "YIELD_VALUE",
    "POP_BLOCK",
    "POP_EXCEPT",
    "STORE_NAME",
    "DELETE_NAME",
    "UNPACK_SEQUENCE",
    "FOR_ITER",
    "UNPACK_EX",
    "STORE_ATTR",
    "DELETE_ATTR",
    "STORE_GLOBAL",
    "DELETE_GLOBAL",
    "LOAD_CONST",
    "LOAD_NAME",
    "BUILD_TUPLE",
    "BUILD_LIST",
    "BUILD_SET",
    "BUILD_MAP",
    "LOAD_ATTR",
    "COMPARE_OP",
    "IMPORT_NAME",
    "IMPORT_FROM",
    "JUMP_FORWARD",
    "JUMP_IF_FALSE_OR_POP",
    "JUMP_IF_TRUE_OR_POP",
    "JUMP_ABSOLUTE",
    "POP_JUMP_IF_FALSE",
    "POP_JUMP_IF_TRUE",
    "LOAD_GLOBAL",
    "IS_OP",
    "CONTAINS_OP",
    "JUMP_IF_NOT_EXC_MATCH",
    "SETUP_FINALLY",
    "LOAD_FAST",
    "STORE_FAST",
    "DELETE_FAST",
    "RAISE_VARARGS",
    "CALL_FUNCTION",
    "MAKE_FUNCTION",
    "BUILD_SLICE",
    "LOAD_CLOSURE",
    "LOAD_DEREF",
    "STORE_DEREF",
    "DELETE_DEREF",
    "CALL_FUNCTION_KW",
    "CALL_FUNCTION_EX",
    "SETUP_WITH",
    "LIST_APPEND",
    "SET_ADD",
    "MAP_ADD",
    "LOAD_CLASSDEREF",
    "EXTENDED_ARG",
    "SETUP_ASYNC_WITH",
    "FORMAT_VALUE",
    "BUILD_CONST_KEY_MAP",
    "BUILD_STRING",
    "LOAD_METHOD",
    "CALL_METHOD",
    "LIST_EXTEND",
    "SET_UPDATE",
    "DICT_MERGE",
    "DICT_UPDATE",
    "BINARY_ADD_REG",
    "BINARY_AND_REG",
    "BINARY_FLOOR_DIVIDE_REG",
    "BINARY_LSHIFT_REG",
    "BINARY_MATRIX_MULTIPLY_REG",
    "BINARY_MODULO_REG",
    "BINARY_MULTIPLY_REG",
    "BINARY_OR_REG",
    "BINARY_POWER_REG",
    "BINARY_RSHIFT_REG",
    "BINARY_SUBSCR_REG",
    "BINARY_SUBTRACT_REG",
    "BINARY_TRUE_DIVIDE_REG",
    "BINARY_XOR_REG",
    "RETURN_VALUE_REG",
    "LOAD_CONST_REG",
    "LOAD_GLOBAL_REG",
    "LOAD_FAST_REG",
    "STORE_FAST_REG",
    "COMPARE_OP_REG",
    "JUMP_IF_FALSE_REG",
    "JUMP_IF_TRUE_REG",
    "UNARY_INVERT_REG",
    "UNARY_NEGATIVE_REG",
    "UNARY_NOT_REG",
    "UNARY_POSITIVE_REG",
    "BUILD_TUPLE_REG",
    "BUILD_MAP_REG",
    "BUILD_LIST_REG",
    "LIST_EXTEND_REG",
    "CALL_FUNCTION_REG",
    "CALL_FUNCTION_KW_REG",
    "INPLACE_ADD_REG",
    "INPLACE_AND_REG",
    "INPLACE_FLOOR_DIVIDE_REG",
    "INPLACE_LSHIFT_REG",
    "INPLACE_MATRIX_MULTIPLY_REG",
    "INPLACE_MODULO_REG",
    "INPLACE_MULTIPLY_REG",
    "INPLACE_OR_REG",
    "INPLACE_POWER_REG",
    "INPLACE_RSHIFT_REG",
    "INPLACE_SUBTRACT_REG",
    "INPLACE_TRUE_DIVIDE_REG",
    "INPLACE_XOR_REG",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown",
    "unknown"
};
