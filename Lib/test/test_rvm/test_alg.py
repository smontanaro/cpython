"""Ever-so-slightly bigger tests, starting with some simple algorithms."""

import unittest

from . import InstructionTest

class AlgTest(InstructionTest):
    @unittest.skip('RAISE_VARARGS not yet implemented')
    def test_fib(self):
        def fib(n):
            if n < 0:
                raise ValueError(f"Fibonacci sequence does not support negative numbers ({n})")
            if n < 2:
                return 1
            return fib(n-1) + fib(n-2)
        (pyvm, rvm) = self.function_helper(fib)
        with self.assertRaises(ValueError):
            rvm(-99)
        self.assertEqual(pyvm(4), rvm(4))
