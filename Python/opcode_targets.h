static void *opcode_targets[256] = {
    &&TARGET_POP_TOP,
    &&TARGET_ROT_TWO,
    &&TARGET_ROT_THREE,
    &&TARGET_DUP_TOP,
    &&TARGET_DUP_TOP_TWO,
    &&TARGET_ROT_FOUR,
    &&TARGET_NOP,
    &&TARGET_UNARY_POSITIVE,
    &&TARGET_UNARY_NEGATIVE,
    &&TARGET_UNARY_NOT,
    &&TARGET_UNARY_INVERT,
    &&TARGET_BINARY_MATRIX_MULTIPLY,
    &&TARGET_INPLACE_MATRIX_MULTIPLY,
    &&TARGET_BINARY_POWER,
    &&TARGET_BINARY_MULTIPLY,
    &&TARGET_BINARY_MODULO,
    &&TARGET_BINARY_ADD,
    &&TARGET_BINARY_SUBTRACT,
    &&TARGET_BINARY_SUBSCR,
    &&TARGET_BINARY_FLOOR_DIVIDE,
    &&TARGET_BINARY_TRUE_DIVIDE,
    &&TARGET_INPLACE_FLOOR_DIVIDE,
    &&TARGET_INPLACE_TRUE_DIVIDE,
    &&TARGET_RERAISE,
    &&TARGET_WITH_EXCEPT_START,
    &&TARGET_GET_AITER,
    &&TARGET_GET_ANEXT,
    &&TARGET_BEFORE_ASYNC_WITH,
    &&TARGET_END_ASYNC_FOR,
    &&TARGET_INPLACE_ADD,
    &&TARGET_INPLACE_SUBTRACT,
    &&TARGET_INPLACE_MULTIPLY,
    &&TARGET_INPLACE_MODULO,
    &&TARGET_STORE_SUBSCR,
    &&TARGET_DELETE_SUBSCR,
    &&TARGET_BINARY_LSHIFT,
    &&TARGET_BINARY_RSHIFT,
    &&TARGET_BINARY_AND,
    &&TARGET_BINARY_XOR,
    &&TARGET_BINARY_OR,
    &&TARGET_INPLACE_POWER,
    &&TARGET_GET_ITER,
    &&TARGET_GET_YIELD_FROM_ITER,
    &&TARGET_PRINT_EXPR,
    &&TARGET_LOAD_BUILD_CLASS,
    &&TARGET_YIELD_FROM,
    &&TARGET_GET_AWAITABLE,
    &&TARGET_LOAD_ASSERTION_ERROR,
    &&TARGET_INPLACE_LSHIFT,
    &&TARGET_INPLACE_RSHIFT,
    &&TARGET_INPLACE_AND,
    &&TARGET_INPLACE_XOR,
    &&TARGET_INPLACE_OR,
    &&TARGET_LIST_TO_TUPLE,
    &&TARGET_RETURN_VALUE,
    &&TARGET_IMPORT_STAR,
    &&TARGET_SETUP_ANNOTATIONS,
    &&TARGET_YIELD_VALUE,
    &&TARGET_POP_BLOCK,
    &&TARGET_POP_EXCEPT,
    &&TARGET_STORE_NAME,
    &&TARGET_DELETE_NAME,
    &&TARGET_UNPACK_SEQUENCE,
    &&TARGET_FOR_ITER,
    &&TARGET_UNPACK_EX,
    &&TARGET_STORE_ATTR,
    &&TARGET_DELETE_ATTR,
    &&TARGET_STORE_GLOBAL,
    &&TARGET_DELETE_GLOBAL,
    &&TARGET_LOAD_CONST,
    &&TARGET_LOAD_NAME,
    &&TARGET_BUILD_TUPLE,
    &&TARGET_BUILD_LIST,
    &&TARGET_BUILD_SET,
    &&TARGET_BUILD_MAP,
    &&TARGET_LOAD_ATTR,
    &&TARGET_COMPARE_OP,
    &&TARGET_IMPORT_NAME,
    &&TARGET_IMPORT_FROM,
    &&TARGET_JUMP_FORWARD,
    &&TARGET_JUMP_IF_FALSE_OR_POP,
    &&TARGET_JUMP_IF_TRUE_OR_POP,
    &&TARGET_JUMP_ABSOLUTE,
    &&TARGET_POP_JUMP_IF_FALSE,
    &&TARGET_POP_JUMP_IF_TRUE,
    &&TARGET_LOAD_GLOBAL,
    &&TARGET_IS_OP,
    &&TARGET_CONTAINS_OP,
    &&TARGET_JUMP_IF_NOT_EXC_MATCH,
    &&TARGET_SETUP_FINALLY,
    &&TARGET_LOAD_FAST,
    &&TARGET_STORE_FAST,
    &&TARGET_DELETE_FAST,
    &&TARGET_RAISE_VARARGS,
    &&TARGET_CALL_FUNCTION,
    &&TARGET_MAKE_FUNCTION,
    &&TARGET_BUILD_SLICE,
    &&TARGET_LOAD_CLOSURE,
    &&TARGET_LOAD_DEREF,
    &&TARGET_STORE_DEREF,
    &&TARGET_DELETE_DEREF,
    &&TARGET_CALL_FUNCTION_KW,
    &&TARGET_CALL_FUNCTION_EX,
    &&TARGET_SETUP_WITH,
    &&TARGET_LIST_APPEND,
    &&TARGET_SET_ADD,
    &&TARGET_MAP_ADD,
    &&TARGET_LOAD_CLASSDEREF,
    &&TARGET_EXTENDED_ARG,
    &&TARGET_SETUP_ASYNC_WITH,
    &&TARGET_FORMAT_VALUE,
    &&TARGET_BUILD_CONST_KEY_MAP,
    &&TARGET_BUILD_STRING,
    &&TARGET_LOAD_METHOD,
    &&TARGET_CALL_METHOD,
    &&TARGET_LIST_EXTEND,
    &&TARGET_SET_UPDATE,
    &&TARGET_DICT_MERGE,
    &&TARGET_DICT_UPDATE,
    &&TARGET_BINARY_POWER_REG,
    &&TARGET_BINARY_MULTIPLY_REG,
    &&TARGET_BINARY_MODULO_REG,
    &&TARGET_BINARY_ADD_REG,
    &&TARGET_BINARY_SUBTRACT_REG,
    &&TARGET_BINARY_SUBSCR_REG,
    &&TARGET_BINARY_FLOOR_DIVIDE_REG,
    &&TARGET_BINARY_TRUE_DIVIDE_REG,
    &&TARGET_RETURN_VALUE_REG,
    &&TARGET_LOAD_CONST_REG,
    &&TARGET_LOAD_GLOBAL_REG,
    &&TARGET_LOAD_FAST_REG,
    &&TARGET_STORE_FAST_REG,
    &&TARGET_COMPARE_OP_REG,
    &&TARGET_JUMP_IF_FALSE_REG,
    &&TARGET_JUMP_IF_TRUE_REG,
    &&TARGET_UNARY_NOT_REG,
    &&TARGET_BUILD_TUPLE_REG,
    &&TARGET_BUILD_LIST_REG,
    &&TARGET_LIST_EXTEND_REG,
    &&TARGET_CALL_FUNCTION_REG,
    &&TARGET_CALL_FUNCTION_KW_REG,
    &&TARGET_UNARY_INVERT_REG,
    &&TARGET_UNARY_NEGATIVE_REG,
    &&TARGET_UNARY_POSITIVE_REG,
    &&TARGET_INPLACE_ADD_REG,
    &&TARGET_INPLACE_AND_REG,
    &&TARGET_INPLACE_FLOOR_DIVIDE_REG,
    &&TARGET_INPLACE_LSHIFT_REG,
    &&TARGET_INPLACE_MATRIX_MULTIPLY_REG,
    &&TARGET_INPLACE_MODULO_REG,
    &&TARGET_INPLACE_MULTIPLY_REG,
    &&TARGET_INPLACE_OR_REG,
    &&TARGET_INPLACE_POWER_REG,
    &&TARGET_INPLACE_RSHIFT_REG,
    &&TARGET_INPLACE_SUBTRACT_REG,
    &&TARGET_INPLACE_TRUE_DIVIDE_REG,
    &&TARGET_INPLACE_XOR_REG,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode,
    &&_unknown_opcode
};
