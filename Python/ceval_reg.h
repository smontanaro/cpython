/* Put register code here then #include it to minimize merge conflicts */

/* extract arg elements out of oparg. */
#define REGARG4(oparg) (oparg >> 24)
#define REGARG3(oparg) ((oparg >> 16) & 0xff)
#define REGARG2(oparg) ((oparg >> 8) & 0xff)
#define REGARG1(oparg) (oparg & 0xff)

/* Disable a few PyVM macros in case I miss something... */

#pragma push_macro("PEEK")
#undef PEEK
#pragma push_macro("TOP")
#undef TOP
#pragma push_macro("POP")
#undef POP

        case TARGET(BINARY_ADD_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *sum;

            if (PyUnicode_CheckExact(left) &&
                     PyUnicode_CheckExact(right)) {
                sum = unicode_concatenate(tstate, left, right, f, next_instr);
                /* unicode_concatenate consumed the ref to left */
                Py_INCREF(left);
            }
            else {
                sum = PyNumber_Add(left, right);
            }
            SETLOCAL(dst, sum);
            if (sum == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_SUBTRACT_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *diff = PyNumber_Subtract(left, right);
            SETLOCAL(dst, diff);
            if (diff == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_SUBSCR_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *container = GETLOCAL(src1);
            PyObject *sub = GETLOCAL(src2);
            PyObject *res = PyObject_GetItem(container, sub);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_POWER_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *exp = GETLOCAL(src2);
            PyObject *base = GETLOCAL(src1);
            PyObject *res = PyNumber_Power(base, exp, Py_None);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_MULTIPLY_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *product = PyNumber_Multiply(left, right);
            SETLOCAL(dst, product);
            if (product == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_MATRIX_MULTIPLY_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *product = PyNumber_MatrixMultiply(left, right);
            SETLOCAL(dst, product);
            if (product == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_TRUE_DIVIDE_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *dividend = GETLOCAL(src1);
            PyObject *divisor = GETLOCAL(src2);
            PyObject *quotient = PyNumber_TrueDivide(dividend, divisor);
            SETLOCAL(dst, quotient);
            if (quotient == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_FLOOR_DIVIDE_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *dividend = GETLOCAL(src1);
            PyObject *divisor = GETLOCAL(src2);
            PyObject *quotient = PyNumber_FloorDivide(dividend, divisor);
            SETLOCAL(dst, quotient);
            if (quotient == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_MODULO_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *dividend = GETLOCAL(src1);
            PyObject *divisor = GETLOCAL(src2);
            PyObject *res;
            if (PyUnicode_CheckExact(dividend) && (
                  !PyUnicode_Check(divisor) || PyUnicode_CheckExact(divisor))) {
              // fast path; string formatting, but not if the RHS is a str subclass
              // (see issue28598)
              res = PyUnicode_Format(dividend, divisor);
            } else {
              res = PyNumber_Remainder(dividend, divisor);
            }
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_AND_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *res = PyNumber_And(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_XOR_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *res = PyNumber_Xor(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_OR_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *res = PyNumber_Or(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_LSHIFT_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *res = PyNumber_Lshift(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(BINARY_RSHIFT_REG): {
            int dst = REGARG3(oparg);
            int src1 = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *res = PyNumber_Rshift(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(RETURN_VALUE_REG): {
            retval = GETLOCAL(oparg);
            /* GETLOCAL(oparg) will be blindly decref'd when registers
               are cleaned up, so this INCREF guarantees we actually have
               something to return. */
            Py_INCREF(retval);
            assert(f->f_iblock == 0);
            f->f_state = FRAME_RETURNED;
            /* not sure what to do with this, so just mimic stack vm for now */
            f->f_stackdepth = 0;
            goto exiting;
        }

        case TARGET(LOAD_CONST_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *value = GETITEM(consts, src);
            Py_INCREF(value);
            SETLOCAL(dst, value);
            DISPATCH();
        }

        case TARGET(LOAD_FAST_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *value = GETLOCAL(src);
            if (value == NULL) {
                format_exc_check_arg(tstate, PyExc_UnboundLocalError,
                                     UNBOUNDLOCAL_ERROR_MSG,
                                     PyTuple_GetItem(co->co_varnames, oparg));
                goto error;
            }
            Py_INCREF(value);
            SETLOCAL(dst, value);
            DISPATCH();
        }

        case TARGET(STORE_FAST_REG): {
            /* LOAD_FAST_REG and STORE_FAST_REG are really the same thing. */
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *value = GETLOCAL(src);
            if (value == NULL) {
                format_exc_check_arg(tstate, PyExc_UnboundLocalError,
                                     UNBOUNDLOCAL_ERROR_MSG,
                                     PyTuple_GetItem(co->co_varnames, oparg));
                goto error;
            }
            Py_INCREF(value);
            SETLOCAL(dst, value);
            DISPATCH();
        }

        case TARGET(LOAD_GLOBAL_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);

            PyObject *name;
            PyObject *v;
            if (PyDict_CheckExact(f->f_globals)
                && PyDict_CheckExact(f->f_builtins))
            {
                OPCACHE_CHECK();
                if (co_opcache != NULL && co_opcache->optimized > 0) {
                    _PyOpcache_LoadGlobal *lg = &co_opcache->u.lg;

                    if (lg->globals_ver ==
                            ((PyDictObject *)f->f_globals)->ma_version_tag
                        && lg->builtins_ver ==
                           ((PyDictObject *)f->f_builtins)->ma_version_tag)
                    {
                        PyObject *ptr = lg->ptr;
                        OPCACHE_STAT_GLOBAL_HIT();
                        assert(ptr != NULL);
                        Py_INCREF(ptr);
                        SETLOCAL(dst, ptr);
                        DISPATCH();
                    }
                }

                name = GETITEM(names, src);
                v = _PyDict_LoadGlobal((PyDictObject *)f->f_globals,
                                       (PyDictObject *)f->f_builtins,
                                       name);
                if (v == NULL) {
                    if (!_PyErr_OCCURRED()) {
                        /* _PyDict_LoadGlobal() returns NULL without raising
                         * an exception if the key doesn't exist */
                        format_exc_check_arg(tstate, PyExc_NameError,
                                             NAME_ERROR_MSG, name);
                    }
                    goto error;
                }

                if (co_opcache != NULL) {
                    _PyOpcache_LoadGlobal *lg = &co_opcache->u.lg;

                    if (co_opcache->optimized == 0) {
                        /* Wasn't optimized before. */
                        OPCACHE_STAT_GLOBAL_OPT();
                    } else {
                        OPCACHE_STAT_GLOBAL_MISS();
                    }

                    co_opcache->optimized = 1;
                    lg->globals_ver =
                        ((PyDictObject *)f->f_globals)->ma_version_tag;
                    lg->builtins_ver =
                        ((PyDictObject *)f->f_builtins)->ma_version_tag;
                    lg->ptr = v; /* borrowed */
                }

                Py_INCREF(v);
            }
            else {
                /* Slow-path if globals or builtins is not a dict */

                /* namespace 1: globals */
                name = GETITEM(names, src);
                v = PyObject_GetItem(f->f_globals, name);
                if (v == NULL) {
                    if (!_PyErr_ExceptionMatches(tstate, PyExc_KeyError)) {
                        goto error;
                    }
                    _PyErr_Clear(tstate);

                    /* namespace 2: builtins */
                    v = PyObject_GetItem(f->f_builtins, name);
                    if (v == NULL) {
                        if (_PyErr_ExceptionMatches(tstate, PyExc_KeyError)) {
                            format_exc_check_arg(
                                        tstate, PyExc_NameError,
                                        NAME_ERROR_MSG, name);
                        }
                        goto error;
                    }
                }
            }
            SETLOCAL(dst, v);
            DISPATCH();
        }

        case TARGET(STORE_GLOBAL_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *name = GETITEM(names, dst);
            PyObject *v = GETLOCAL(src);
            int err;
            err = PyDict_SetItem(f->f_globals, name, v);
            if (err != 0)
                goto error;
            DISPATCH();
        }

        case TARGET(CONTAINS_OP_REG): {
            int dst = REGARG4(oparg);
            int src1 = REGARG3(oparg);
            int src2 = REGARG2(oparg);
            int contop = REGARG1(oparg);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            int res = PySequence_Contains(right, left);
            if (res < 0) {
                goto error;
            }
            PyObject *b = (res^contop) ? Py_True : Py_False;
            Py_INCREF(b);
            SETLOCAL(dst, b);
            DISPATCH();
        }

        case TARGET(COMPARE_OP_REG): {
            int dst = REGARG4(oparg);
            int src1 = REGARG3(oparg);
            int src2 = REGARG2(oparg);
            int cmpop = REGARG1(oparg);
            assert(cmpop <= Py_GE);
            PyObject *left = GETLOCAL(src1);
            PyObject *right = GETLOCAL(src2);
            PyObject *res = PyObject_RichCompare(left, right, cmpop);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(JUMP_IF_FALSE_REG): {
            int target = REGARG3(oparg) << 8 | REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *cond = GETLOCAL(src);
            int err;
            if (cond == Py_True) {
                DISPATCH();
            }
            if (cond == Py_False) {
                JUMPTO(target);
                DISPATCH();
            }
            err = PyObject_IsTrue(cond);
            if (err > 0)
                ;
            else if (err == 0)
                JUMPTO(target);
            else
                goto error;
            DISPATCH();
        }

        case TARGET(JUMP_IF_TRUE_REG): {
            int target = REGARG3(oparg) << 8 | REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *cond = GETLOCAL(src);
            int err;
            if (cond == Py_False) {
                DISPATCH();
            }
            if (cond == Py_True) {
                JUMPTO(target);
                DISPATCH();
            }
            err = PyObject_IsTrue(cond);
            if (err > 0)
                JUMPTO(target);
            else if (err == 0)
                ;
            else
                goto error;
            DISPATCH();
        }

        case TARGET(UNARY_NOT_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *value = GETLOCAL(src);
            int err = PyObject_IsTrue(value);
            if (err == 0) {
                Py_INCREF(Py_True);
                SETLOCAL(dst, Py_True);
                DISPATCH();
            }
            else if (err > 0) {
                Py_INCREF(Py_False);
                SETLOCAL(dst, Py_False);
                DISPATCH();
            }
            goto error;
        }

        case TARGET(BUILD_SET_REG): {
            /* registers go from src to src+len */
            int dst = REGARG2(oparg);
            int len = REGARG1(oparg);
            PyObject *set = PySet_New(NULL);
            int err = 0;
            if (set == NULL)
                goto error;
            while (--len >= 0) {
                PyObject *item = GETLOCAL(dst+len);
                Py_INCREF(item);
                if (err == 0)
                    err = PySet_Add(set, item);
            }
            SETLOCAL(dst, set);
            DISPATCH();
        }

        case TARGET(BUILD_TUPLE_REG): {
            /* registers go from src to src+len */
            int dst = REGARG2(oparg);
            int len = REGARG1(oparg);
            PyObject *tup = PyTuple_New(len);
            if (tup == NULL)
                goto error;
            while (--len >= 0) {
                PyObject *item = GETLOCAL(dst+len);
                Py_INCREF(item);
                PyTuple_SET_ITEM(tup, len, item);
            }
            SETLOCAL(dst, tup);
            DISPATCH();
        }

        case TARGET(BUILD_MAP_REG): {
            int dst = REGARG2(oparg);
            int size = REGARG1(oparg);
            int start = dst + 2 * size;
            Py_ssize_t i;
            PyObject *map = _PyDict_NewPresized((Py_ssize_t)size);
            if (map == NULL)
                goto error;
            for (i = size; i > 0; i--) {
                int err;
                PyObject *key = GETLOCAL(start - 2*i);
                PyObject *value = GETLOCAL(start - 2*i - 1);
                err = PyDict_SetItem(map, key, value);
                if (err != 0) {
                    Py_DECREF(map);
                    goto error;
                }
            }

            SETLOCAL(dst, map);
            DISPATCH();
        }

        case TARGET(BUILD_LIST_REG): {
            /* registers go from src to src+len */
            int dst = REGARG2(oparg);
            int len = REGARG1(oparg);
            PyObject *list = PyList_New(len);
            if (list == NULL)
                goto error;
            while (--len >= 0) {
                PyObject *item = GETLOCAL(dst+len);
                Py_INCREF(item);
                PyList_SET_ITEM(list, len, item);
            }
            SETLOCAL(dst, list);
            DISPATCH();
        }

        case TARGET(LIST_EXTEND_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *iterable = GETLOCAL(src);
            PyObject *list = GETLOCAL(dst);
            PyObject *none_val = _PyList_Extend((PyListObject *)list, iterable);
            if (none_val == NULL) {
                if (_PyErr_ExceptionMatches(tstate, PyExc_TypeError) &&
                   (Py_TYPE(iterable)->tp_iter == NULL && !PySequence_Check(iterable)))
                {
                    _PyErr_Clear(tstate);
                    _PyErr_Format(tstate, PyExc_TypeError,
                          "Value after * must be an iterable, not %.200s",
                          Py_TYPE(iterable)->tp_name);
                }
                Py_DECREF(iterable);
                goto error;
            }
            Py_DECREF(none_val);
            DISPATCH();
        }

        case TARGET(CALL_FUNCTION_REG): {
            PyObject **sp, *res;
            int dst = REGARG2(oparg);
            int nargs = REGARG1(oparg);
            sp = &GETLOCAL(dst + nargs + 1);
            res = call_function(tstate, &sp, nargs, NULL);
            SETLOCAL(dst, res);
            if (res == NULL) {
                goto error;
            }
            DISPATCH();
        }

        case TARGET(CALL_FUNCTION_KW_REG): {
            PyObject **sp, *res, *names;
            int dst = REGARG3(oparg);
            /* register containing kw names tuple */
            int nreg = REGARG2(oparg);
            int nargs = REGARG1(oparg);

            names = GETLOCAL(nreg);
            Py_INCREF(names);
            Py_CLEAR(GETLOCAL(nreg));
            assert(PyTuple_Check(names));
            assert(PyTuple_GET_SIZE(names) <= nargs);
            /* We assume without checking that names contains only strings */
            sp = &GETLOCAL(dst + nargs + 1);
            res = call_function(tstate, &sp, nargs, names);
            Py_DECREF(names);
            SETLOCAL(dst, res);

            if (res == NULL) {
                goto error;
            }
            DISPATCH();
        }

        case TARGET(UNARY_INVERT_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *value = GETLOCAL(src);
            PyObject *res = PyNumber_Invert(value);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(UNARY_NEGATIVE_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *value = GETLOCAL(src);
            PyObject *res = PyNumber_Negative(value);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(UNARY_POSITIVE_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *value = GETLOCAL(src);
            PyObject *res = PyNumber_Positive(value);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_OR_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceOr(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_POWER_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlacePower(left, right, Py_None);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_MULTIPLY_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceMultiply(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_MATRIX_MULTIPLY_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceMatrixMultiply(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_TRUE_DIVIDE_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceTrueDivide(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_FLOOR_DIVIDE_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceFloorDivide(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_MODULO_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceRemainder(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_ADD_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *sum;
            if (PyUnicode_CheckExact(left) && PyUnicode_CheckExact(right)) {
                sum = unicode_concatenate(tstate, left, right, f, next_instr);
                /* unicode_concatenate consumed the ref to left */
            }
            else {
                sum = PyNumber_InPlaceAdd(left, right);
            }
            SETLOCAL(dst, sum);
            if (sum == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_LSHIFT_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceLshift(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_RSHIFT_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceRshift(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_AND_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceAnd(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_XOR_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceXor(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(INPLACE_SUBTRACT_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *left = GETLOCAL(dst);
            PyObject *right = GETLOCAL(src);
            PyObject *res = PyNumber_InPlaceSubtract(left, right);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(LOAD_ATTR_REG): {
            int dst = REGARG3(oparg);
            int src = REGARG2(oparg);
            int attr = REGARG1(oparg);
            PyObject *name = GETITEM(names, attr);
            PyObject *owner = GETLOCAL(src);
            PyObject *res = PyObject_GetAttr(owner, name);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(STORE_ATTR_REG): {
            int src1 = REGARG3(oparg);
            int attr = REGARG2(oparg);
            int src2 = REGARG1(oparg);
            PyObject *name = GETITEM(names, attr);
            PyObject *owner = GETLOCAL(src1);
            PyObject *v = GETLOCAL(src2);
            int err;
            err = PyObject_SetAttr(owner, name, v);
            if (err != 0)
                goto error;
            DISPATCH();
        }

        case TARGET(DELETE_ATTR_REG): {
            int src = REGARG2(oparg);
            int attr = REGARG1(oparg);
            PyObject *name = GETITEM(names, attr);
            PyObject *owner = GETLOCAL(src);
            int err;
            err = PyObject_SetAttr(owner, name, (PyObject *)NULL);
            if (err != 0)
                goto error;
            DISPATCH();
        }

        case TARGET(GET_ITER_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *iterable = GETLOCAL(src);
            PyObject *iter = PyObject_GetIter(iterable);
            SETLOCAL(dst, iter);
            if (iter == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(FOR_ITER_REG): {
            int dst = REGARG4(oparg);
            int src = REGARG3(oparg);
            int jumpby = REGARG2(oparg) << 8 | REGARG1(oparg);
            PyObject *iter = GETLOCAL(src);
            PyObject *next = (*Py_TYPE(iter)->tp_iternext)(iter);
            if (next != NULL) {
                SETLOCAL(dst, next);
                DISPATCH();
            }
            if (_PyErr_Occurred(tstate)) {
                if (!_PyErr_ExceptionMatches(tstate, PyExc_StopIteration)) {
                    goto error;
                }
                else if (tstate->c_tracefunc != NULL) {
                    call_exc_trace(tstate->c_tracefunc, tstate->c_traceobj, tstate, f);
                }
                _PyErr_Clear(tstate);
            }
            /* iterator ended normally */
            JUMPBY(jumpby);
            DISPATCH();
        }

        case TARGET(IMPORT_NAME_REG): {
            int dst = REGARG4(oparg);
            int n = REGARG3(oparg);
            int src = REGARG2(oparg);
            int nm = REGARG1(oparg);
            PyObject *name = GETITEM(names, nm);
            PyObject *fromlist = GETLOCAL(src);
            PyObject *level = GETLOCAL(n);
            PyObject *res = import_name(tstate, f, name, fromlist, level);
            SETLOCAL(dst, res);
            if (res == NULL)
                goto error;
            DISPATCH();
        }

        case TARGET(DICT_MERGE_REG): {
            PyObject *update = GETLOCAL(REGARG1(oparg));
            PyObject *dict = GETLOCAL(REGARG2(oparg));

            if (_PyDict_MergeEx(dict, update, 2) < 0) {
                _PyErr_Format(tstate, PyExc_TypeError,
                              "argument after ** must be a mapping, not %.200s",
                              Py_TYPE(update)->tp_name);
                goto error;
            }
            PREDICT(CALL_FUNCTION_EX);
            DISPATCH();
        }

        case TARGET(DICT_UPDATE_REG): {
            int dst = REGARG2(oparg);
            int src = REGARG1(oparg);
            PyObject *update = GETLOCAL(src);
            PyObject *dict = GETLOCAL(dst);

            if (PyDict_Update(dict, update) < 0) {
                if (_PyErr_ExceptionMatches(tstate, PyExc_AttributeError)) {
                    _PyErr_Format(tstate, PyExc_TypeError,
                                    "'%.200s' object is not a mapping",
                                    Py_TYPE(update)->tp_name);
                }
                goto error;
            }
            DISPATCH();
        }

        case TARGET(CALL_FUNCTION_EX_REG): {
            int dst = REGARG4(oparg);
            int kw = REGARG3(oparg);
            int cargs = REGARG2(oparg);
            int fn = REGARG1(oparg);
            PyObject *func, *callargs, *kwargs = NULL, *result;
            if (oparg & 0x01) {
                kwargs = GETLOCAL(kw);
                if (!PyDict_CheckExact(kwargs)) {
                    PyObject *d = PyDict_New();
                    if (d == NULL)
                        goto error;
                    if (_PyDict_MergeEx(d, kwargs, 2) < 0) {
                        Py_DECREF(d);
                        _PyErr_Format(tstate, SECOND(), kwargs);
                        goto error;
                    }
                    kwargs = d;
                }
                assert(PyDict_CheckExact(kwargs));
            }
            callargs = GETLOCAL(cargs);
            func = GETLOCAL(fn);
            if (!PyTuple_CheckExact(callargs)) {
                if (check_args_iterable(tstate, func, callargs) < 0) {
                    Py_DECREF(callargs);
                    goto error;
                }
                Py_SETREF(callargs, PySequence_Tuple(callargs));
                if (callargs == NULL) {
                    goto error;
                }
            }
            assert(PyTuple_CheckExact(callargs));

            result = do_call_core(tstate, func, callargs, kwargs);

            SETLOCAL(dst, result);
            if (result == NULL) {
                goto error;
            }
            DISPATCH();
        }


        /* case TARGET(YIELD_VALUE_REG): { */
        /*     int src = REGARG1(oparg); */
        /*     retval = GETLOCAL(src); */

        /*     if (co->co_flags & CO_ASYNC_GENERATOR) { */
        /*         PyObject *w = _PyAsyncGenValueWrapperNew(retval); */
        /*         Py_DECREF(retval); */
        /*         if (w == NULL) { */
        /*             retval = NULL; */
        /*             goto error; */
        /*         } */
        /*         retval = w; */
        /*     } */

        /*     f->f_state = FRAME_SUSPENDED; */
        /*     f->f_stackdepth = stack_pointer-f->f_valuestack; */
        /*     goto exiting; */
        /* } */

#pragma pop_macro("POP")
#pragma pop_macro("TOP")
#pragma pop_macro("PEEK")
