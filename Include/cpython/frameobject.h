/* Frame object interface */

#ifndef Py_CPYTHON_FRAMEOBJECT_H
#  error "this header file must not be included directly"
#endif

#ifdef __cplusplus
extern "C" {
#endif

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
^                                                           ^
|                                                           |
+-- f_localsplus                                            +-- f_valuestack

# If we move the stack next to the locals, we can treat the stack
  space as a register file. ISTR Tim Peters saying in the old
  rattlesnake days that the number of registers would be no greater
  than the max stack size.

+-------------------+-------------------+-------------------+-------------------+
|                   |                   |                   |                   |
| fastlocals        | stack             | cells             | frees             |
|  len(co_nlocals)  |  len(co_stacksize)|  len(co_cellvars) |  len(co_freevars) |
+-------------------+-------------------+-------------------+-------------------+
^                   ^
|                   |
+-- f_localsplus    +-- f_valuestack

# This will require some adjustment to the offset to the start of cell
  and free variables, but it seems unlikely to cause much widespread
  damage. I think a few bits of frameobject.c and ceval.c will ened to
  be tweaked, but nothing else.

# One question needs to be answered though. When cell and free
  variables arrived on the scene, why didn't they just get tacked onto
  the end of the stack space? We know the maximum size to which the
  stack can grow, and allocate that much space. Having cells and frees
  at the end of the allocated space wouldn't add risk that the stack
  would crash into them. (If that was a concern, just allocate one
  more slot for the stack and make sure it was initialized to a known
  bogus value.)

*/

typedef struct _frame {
    PyObject_VAR_HEAD
    struct _frame *f_back;      /* previous frame, or NULL */
    PyCodeObject *f_code;       /* code segment */
    PyObject *f_builtins;       /* builtin symbol table (PyDictObject) */
    PyObject *f_globals;        /* global symbol table (PyDictObject) */
    PyObject *f_locals;         /* local symbol table (any mapping) */
    PyObject **f_valuestack;    /* points after the last local */
    /* Next free slot in f_valuestack.  Frame creation sets to f_valuestack.
       Frame evaluation usually NULLs it, but a frame that yields sets it
       to the current stack top. */
    PyObject **f_stacktop;
    PyObject *f_trace;          /* Trace function */
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
    char f_executing;           /* whether the frame is still executing */
    PyTryBlock f_blockstack[CO_MAXBLOCKS]; /* for try and loop blocks */
    PyObject *f_localsplus[1];  /* locals+stack, dynamically sized */
} PyFrameObject;


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

PyAPI_FUNC(int) PyFrame_ClearFreeList(void);

PyAPI_FUNC(void) _PyFrame_DebugMallocStats(FILE *out);

/* Return the line of code the frame is currently executing. */
PyAPI_FUNC(int) PyFrame_GetLineNumber(PyFrameObject *);

#ifdef __cplusplus
}
#endif
