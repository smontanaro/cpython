"""Not yet implemented test cases."""

import unittest

from . import InstructionTest

class TBDTest(InstructionTest):
    @unittest.skip('RAISE_VARAGS_REG not yet implemented')
    def test_raise(self):
        def raise_():
            raise ValueError
        (pyvm, rvm) = self.function_helper(raise_)
        try:
            pyvm()
        except ValueError:
            pyvm_result = "pass"
        else:
            pyvm_result = "fail"
        try:
            rvm()
        except ValueError:
            rvm_result = "pass"
        else:
            rvm_result = "fail"
        self.assertTrue(pyvm_result == "pass" == rvm_result)

    @unittest.skip('MAKE_FUNCTION_REG, MAP_ADD_REG not yet implemented')
    def test_dictcomp(self):
        def dictcomp(keys, vals):
            return {key: val for (key, val) in zip(keys, vals)}
        (pyvm, rvm) = self.function_helper(dictcomp)
        keys = (1, 2, 3)
        vals = "abc"
        self.assertEqual(pyvm(keys, vals), rvm(keys, vals))

    @unittest.skip('LOAD_METHOD_REG, CALL_METHOD_REG not yet implemented')
    def test_method(self):
        class X:
            def meth1(self):
                return "<X>"
            def meth2(self):
                return self.meth1()
        x = X()
        (pyvm, rvm) = self.function_helper(x.meth2)
        self.assertEqual(pyvm(), rvm())

    @unittest.skip('LIST_APPEND_REG not yet implemented')
    def test_list_append(self):
        def append(s):
            return [c for c in s]
        (pyvm, rvm) = self.function_helper(append)
        self.assertEqual(pyvm("abcd"), rvm("abcd"))

    @unittest.skip('LIST_TO_TUPLE_REG not yet implemented')
    def test_list_to_tuple(self):
        def func1(key, *args, **kw):
            return (key, args, kw)
        def func2(key, *args, **kw):
            return func1(key, *args, **kw)
        (pyvm, rvm) = self.function_helper(func2)
        self.assertEqual(pyvm("abcd", 1, 2, 3, k1=0, k2=1),
                         rvm("abcd", 1, 2, 3, k1=0, k2=1))

    @unittest.skip("STORE_DEREF and LOAD_CLOSURE aren't yet implemented, nor is inner() translated")
    def test_deref(self):
        def outer(a):
            loc = a
            def inner():
                return loc
            return inner()
