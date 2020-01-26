/* bits shared between compile.c and regcompile.c ONLY */

#define DEFAULT_BLOCK_SIZE 16
#define DEFAULT_BLOCKS 8
#define DEFAULT_CODE_SIZE 128
#define DEFAULT_LNOTAB_SIZE 16

#define COMP_GENEXP   0
#define COMP_LISTCOMP 1
#define COMP_SETCOMP  2
#define COMP_DICTCOMP 3

struct instr {
    unsigned i_jabs : 1;
    unsigned i_jrel : 1;
    unsigned char i_opcode;
    int i_oparg;
    struct basicblock_ *i_target; /* target block (if jump instruction) */
    int i_lineno;
};

typedef struct basicblock_ {
    /* Each basicblock in a compilation unit is linked via b_list in the
       reverse order that the block are allocated.  b_list points to the next
       block, not to be confused with b_next, which is next by control flow. */
    struct basicblock_ *b_list;
    /* number of instructions used */
    int b_iused;
    /* length of instruction array (b_instr) */
    int b_ialloc;
    /* pointer to an array of instructions, initially NULL */
    struct instr *b_instr;
    /* If b_next is non-NULL, it is a pointer to the next
       block reached by normal control flow. */
    struct basicblock_ *b_next;
    /* b_seen is used to perform a DFS of basicblocks. */
    unsigned b_seen : 1;
    /* b_return is true if a RETURN_VALUE opcode is inserted. */
    unsigned b_return : 1;
    /* depth of stack upon entry of block, computed by stackdepth() */
    int b_startdepth;
    /* instruction offset for block, computed by assemble_jump_offsets() */
    int b_offset;
} basicblock;

/* fblockinfo tracks the current frame block.

A frame block is used to handle loops, try/except, and try/finally.
It's called a frame block to distinguish it from a basic block in the
compiler IR.
*/

enum fblocktype { WHILE_LOOP, FOR_LOOP, EXCEPT, FINALLY_TRY, FINALLY_END,
                  WITH, ASYNC_WITH, HANDLER_CLEANUP, POP_VALUE };

struct fblockinfo {
    enum fblocktype fb_type;
    basicblock *fb_block;
    /* (optional) type-specific exit or cleanup block */
    basicblock *fb_exit;
    /* (optional) additional information required for unwinding */
    void *fb_datum;
};

enum {
    COMPILER_SCOPE_MODULE,
    COMPILER_SCOPE_CLASS,
    COMPILER_SCOPE_FUNCTION,
    COMPILER_SCOPE_ASYNC_FUNCTION,
    COMPILER_SCOPE_LAMBDA,
    COMPILER_SCOPE_COMPREHENSION,
};

/* The following items change on entry and exit of code blocks.
   They must be saved and restored when returning to a block.
*/
struct compiler_unit {
    PySTEntryObject *u_ste;

    PyObject *u_name;
    PyObject *u_qualname;  /* dot-separated qualified name (lazy) */
    int u_scope_type;

    /* The following fields are dicts that map objects to
       the index of them in co_XXX.      The index is used as
       the argument for opcodes that refer to those collections.
    */
    PyObject *u_consts;    /* all constants */
    PyObject *u_names;     /* all names */
    PyObject *u_varnames;  /* local variables */
    PyObject *u_cellvars;  /* cell variables */
    PyObject *u_freevars;  /* free variables */

    PyObject *u_private;        /* for private name mangling */

    Py_ssize_t u_argcount;        /* number of arguments for block */
    Py_ssize_t u_posonlyargcount;        /* number of positional only arguments for block */
    Py_ssize_t u_kwonlyargcount; /* number of keyword only arguments for block */
    /* Pointer to the most recently allocated block.  By following b_list
       members, you can reach all early allocated blocks. */
    basicblock *u_blocks;
    basicblock *u_curblock; /* pointer to current block */

    int u_nfblocks;
    struct fblockinfo u_fblock[CO_MAXBLOCKS];

    int u_firstlineno; /* the first lineno of the block */
    int u_lineno;          /* the lineno for the current stmt */
    int u_col_offset;      /* the offset of the current stmt */
    int u_lineno_set;  /* boolean to indicate whether instr
                          has been generated with current lineno */
};

/* This struct captures the global state of a compilation.

The u pointer points to the current compilation unit, while units
for enclosing blocks are stored in c_stack.     The u and c_stack are
managed by compiler_enter_scope() and compiler_exit_scope().

Note that we don't track recursion levels during compilation - the
task of detecting and rejecting excessive levels of nesting is
handled by the symbol analysis pass.

*/

struct compiler {
    PyObject *c_filename;
    struct symtable *c_st;
    PyFutureFeatures *c_future; /* pointer to module's __future__ */
    PyCompilerFlags *c_flags;

    int c_optimize;              /* optimization level */
    int c_interactive;           /* true if in interactive mode */
    int c_nestlevel;
    int c_do_not_emit_bytecode;  /* The compiler won't emit any bytecode
                                    if this value is different from zero.
                                    This can be used to temporarily visit
                                    nodes without emitting bytecode to
                                    check only errors. */

    PyObject *c_const_cache;     /* Python dict holding all constants,
                                    including names tuple */
    struct compiler_unit *u; /* compiler state for current block */
    PyObject *c_stack;           /* Python list holding compiler_unit ptrs */
    PyArena *c_arena;            /* pointer to memory allocation arena */
};
