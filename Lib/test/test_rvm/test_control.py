
import sys
import unittest

from . import InstructionTest

class RaiseTest(InstructionTest):
    def test_raise_simple(self):
        def raise_simple():
            raise ValueError
        (pyvm, rvm) = self.function_helper(raise_simple)
        with self.assertRaises(ValueError):
            rvm()
