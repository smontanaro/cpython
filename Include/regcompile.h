#ifndef Py_REGCOMPILE_H
#define Py_REGCOMPILE_H

#include "compile.h"

#ifndef Py_LIMITED_API
#include "code.h"

#ifdef __cplusplus
extern "C" {
#endif

PyAPI_FUNC(PyCodeObject *) _PyAST_CompileObjectR(
    struct _mod *mod,
    PyObject *filename,
    PyCompilerFlags *flags,
    int optimize,
    PyArena *arena);

#ifdef __cplusplus
}
#endif

#endif /* !Py_LIMITED_API */

#endif /* !Py_REGCOMPILE_H */
