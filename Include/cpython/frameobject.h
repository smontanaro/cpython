/* Frame object interface */

#ifndef Py_CPYTHON_FRAMEOBJECT_H
#  error "this header file must not be included directly"
#endif

/* These values are chosen so that the inline functions below all
 * compare f_state to zero.
 */
enum _framestate {
    FRAME_CREATED = -2,
    FRAME_SUSPENDED = -1,
    FRAME_EXECUTING = 0,
    FRAME_RETURNED = 1,
    FRAME_UNWINDING = 2,
    FRAME_RAISED = 3,
    FRAME_CLEARED = 4
};

typedef signed char PyFrameState;

typedef struct {
    int b_type;                 /* what kind of block this is */
    int b_handler;              /* where to jump to find handler */
    int b_level;                /* value stack level to pop to */
} PyTryBlock;

/*

# Layout of locals, cells, frees, stack in current CPython:

+-------------------+-------------------+-------------------+-------------------+
|                   |                   |                   |                   |
| fastlocals        | cells             | frees             | stack             |
|  len(co_nlocals)  |  len(co_cellvars) |  len(co_freevars) |  len(co_stacksize)|
+-------------------+-------------------+-------------------+-------------------+
^                   ^                                       ^
|                   |                                       |
+-- f_localsplus    +-- f_cellvars                          +-- f_valuestack

If we move the stack next to the locals, we can treat the locals+stack
as a contiguous register file. ISTR Tim Peters saying in the old
rattlesnake days that the number of registers would be no greater than
the max stack size. This will eliminate LOAD_FAST_REG and
STORE_FAST_REG opcodes which should be a good performance win.

+-------------------+-------------------+-------------------+-------------------+
|                   |                   |                   |                   |
| fastlocals        | stack             | cells             | frees             |
|  len(co_nlocals)  |  len(co_stacksize)|  len(co_cellvars) |  len(co_freevars) |
+-------------------+-------------------+-------------------+-------------------+
^                   ^                   ^
|                   |                   |
+-- f_localsplus    +-- f_valuestack    +-- f_cellvars

This requires some adjustment to the offset to the start of cell and
free variables. My first attempt failed miserably. On my second
attempt, I added the above f_cellvars slot to the _frame struct and am
proceeding more carefully.  It took a bit of effort to work this out,
but I think it's working now (tests pass, at least). See
_PyFrame_New_NoTrack.

It wasn't obvious to me why cells and free vars were added adjacent to
locals. It does seem that in certain places, locals, cells and frees
are all treated as one, so having them adjacent in memory makes things
a touch simpler, but separating into separate for loops (for example)
isn't much extra work, mostly confined to frameobject.c.

*/

struct _frame {
    PyObject_VAR_HEAD
    struct _frame *f_back;      /* previous frame, or NULL */
    PyCodeObject *f_code;       /* code segment */
    PyObject *f_builtins;       /* builtin symbol table (PyDictObject) */
    PyObject *f_globals;        /* global symbol table (PyDictObject) */
    PyObject *f_locals;         /* local symbol table (any mapping) */
    PyObject **f_valuestack;    /* points after the last local */
    PyObject **f_cellvars;      /* points to the first cell/free var */
    PyObject *f_trace;          /* Trace function */
    int f_stackdepth;           /* Depth of value stack */
    char f_trace_lines;         /* Emit per-line trace events? */
    char f_trace_opcodes;       /* Emit per-opcode trace events? */

    /* Borrowed reference to a generator, or NULL */
    PyObject *f_gen;

    int f_lasti;                /* Last instruction if called */
    /* Call PyFrame_GetLineNumber() instead of reading this field
       directly.  As of 2.3 f_lineno is only valid when tracing is
       active (i.e. when f_trace is set).  At other times we use
       PyCode_Addr2Line to calculate the line from the current
       bytecode index. */
    int f_lineno;               /* Current line number */
    int f_iblock;               /* index in f_blockstack */
    PyFrameState f_state;       /* What state the frame is in */
    PyTryBlock f_blockstack[CO_MAXBLOCKS]; /* for try and loop blocks */
    PyObject *f_localsplus[1];  /* locals+stack, dynamically sized */
};

static inline int _PyFrame_IsRunnable(struct _frame *f) {
    return f->f_state < FRAME_EXECUTING;
}

static inline int _PyFrame_IsExecuting(struct _frame *f) {
    return f->f_state == FRAME_EXECUTING;
}

static inline int _PyFrameHasCompleted(struct _frame *f) {
    return f->f_state > FRAME_EXECUTING;
}

/* Standard object interface */

PyAPI_DATA(PyTypeObject) PyFrame_Type;

#define PyFrame_Check(op) Py_IS_TYPE(op, &PyFrame_Type)

PyAPI_FUNC(PyFrameObject *) PyFrame_New(PyThreadState *, PyCodeObject *,
                                        PyObject *, PyObject *);

/* only internal use */
PyFrameObject* _PyFrame_New_NoTrack(PyThreadState *, PyCodeObject *,
                                    PyObject *, PyObject *);


/* The rest of the interface is specific for frame objects */

/* Block management functions */

PyAPI_FUNC(void) PyFrame_BlockSetup(PyFrameObject *, int, int, int);
PyAPI_FUNC(PyTryBlock *) PyFrame_BlockPop(PyFrameObject *);

/* Conversions between "fast locals" and locals in dictionary */

PyAPI_FUNC(void) PyFrame_LocalsToFast(PyFrameObject *, int);

PyAPI_FUNC(int) PyFrame_FastToLocalsWithError(PyFrameObject *f);
PyAPI_FUNC(void) PyFrame_FastToLocals(PyFrameObject *);

PyAPI_FUNC(void) _PyFrame_DebugMallocStats(FILE *out);

PyAPI_FUNC(PyFrameObject *) PyFrame_GetBack(PyFrameObject *frame);
