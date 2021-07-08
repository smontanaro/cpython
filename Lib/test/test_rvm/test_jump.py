
import unittest

from . import InstructionTest

class JumpTest(InstructionTest):
    def test_jump_if_false(self):
        def jump_if_false(a):
            if a:
                return 42
            return 41
        (pyvm, rvm) = self.function_helper(jump_if_false)
        self.assertEqual(pyvm(7), rvm(7))
        self.assertEqual(pyvm(0), rvm(0))
        self.assertEqual(pyvm(()), rvm(()))
        self.assertEqual(pyvm(False), rvm(False))
        self.assertEqual(pyvm(True), rvm(True))

    def test_jump_if_true(self):
        def jump_if_true(a):
            if not a:
                return 42
            return 43
        (pyvm, rvm) = self.function_helper(jump_if_true)
        self.assertEqual(pyvm(7), rvm(7))
        self.assertEqual(pyvm(0), rvm(0))
        self.assertEqual(pyvm(()), rvm(()))
        self.assertEqual(pyvm(False), rvm(False))
        self.assertEqual(pyvm(True), rvm(True))

    @unittest.skip("broken")
    def test_simple_branch_function(self):
        def branch_func(a):
            if a > 4:
                return a
            if a in (1, 2):
                return a
            b = a + 4
            return b
        (pyvm, rvm) = self.function_helper(branch_func)
        self.assertEqual(pyvm(7), rvm(7))
        self.assertEqual(pyvm(1), rvm(1))
        self.assertEqual(pyvm(0), rvm(0))
