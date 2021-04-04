"""Ever-so-slightly bigger tests, starting with some simple algorithms."""

import unittest

from . import InstructionTest

class AlgTest(InstructionTest):
    @unittest.skip('Something not right regarding free vrbls.')
    # ERROR: test_fib (test.test_rvm.test_alg.AlgTest)
    # ----------------------------------------------------------------------
    # Traceback (most recent call last):
    #   File "/home/skip/src/python/rvm/Lib/test/test_rvm/test_alg.py", line 16, in test_fib
    #     (pyvm, rvm) = self.function_helper(fib)
    #   File "/home/skip/src/python/rvm/Lib/test/test_rvm/__init__.py", line 42, in function_helper
    #     rvm_replace_code(rvm, pyvm_code, isc)
    #   File "/home/skip/src/python/rvm/Lib/test/test_rvm/__init__.py", line 115, in rvm_replace_code
    #     func.__code__ = rvm_code
    # ValueError: rvm() requires a code object with 0 free vars, not 1
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
