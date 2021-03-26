
import unittest

from . import InstructionTest

class CallTest(InstructionTest):
    def test_callfunc(self):
        def callfunc():
            return [bin(2796202), list(enumerate("1234", 2))]
        (pyvm, rvm) = self.function_helper(callfunc)
        self.assertEqual(pyvm(), rvm())

    @unittest.skip('currently broken')
    def test_callfunc_kw(self):
        (pyvm, rvm) = self.function_helper(_callfunc_kw)
        self.assertEqual(pyvm(), rvm())

    @unittest.skip('currently broken')
    def test_callfunc_protected_reg(self):
        (pyvm, rvm) = self.function_helper(_callfunc_protected_reg)
        self.assertEqual(pyvm(13.0), rvm(13.0))

# Still required to be at top level for now...

def _test_cf(a, b, c):
    return a + b + c

def _callfunc_protected_reg(a):
    return _test_cf(a, a ** 2, a / 7)

def _kw_func(a, b=None):
    return (a, b)

def _callfunc_kw():
    return _kw_func(14, b="hello world")
