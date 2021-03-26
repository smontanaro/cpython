
import unittest

from . import InstructionTest

class UnaryOpTest(InstructionTest):
    def test_negative(self):
        def negative(val):
            return -val
        (pyvm, rvm) = self.function_helper(negative)
        for val in (5, -99):
            self.assertEqual(pyvm(val), rvm(val))

    def test_not(self):
        def not_(val):
            return not val
        (pyvm, rvm) = self.function_helper(not_)
        for val in (5, None, ()):
            self.assertEqual(pyvm(val), rvm(val))

    def test_positive(self):
        def positive(val):
            return +val
        (pyvm, rvm) = self.function_helper(positive)
        for val in (5, -99):
            self.assertEqual(pyvm(val), rvm(val))
