
import sys
import unittest

from . import InstructionTest

class LoadStoreTest(InstructionTest):
    def test_load_fast(self):
        def load_fast(a, b):
            a = a
            a = b
            b = a
            return a
        (pyvm, rvm) = self.function_helper(load_fast)
        self.assertEqual(pyvm(12, -1), rvm(12, -1))

    def test_load_const(self):
        def load_const():
            return 5
        (pyvm, rvm) = self.function_helper(load_const)
        print(5, sys.getrefcount(5))
        result = rvm()
        print(5, sys.getrefcount(5))
