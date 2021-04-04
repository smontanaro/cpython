
import unittest

from . import InstructionTest

class StringTest(InstructionTest):
    def test_build_string(self):
        def build_string():
            return f""
        (pyvm, rvm) = self.function_helper(build_string)
        self.assertEqual(pyvm(), rvm())

    def test_format_value(self):
        def format_value(a, b):
            return f"{a} 4 {b:.2f} {(a+b)!r}"
        (pyvm, rvm) = self.function_helper(format_value)
        self.assertEqual(pyvm(14, -3), rvm(14, -3))

    @unittest.skip("looks like perhaps a ref count error...")
    def test_fstring(self):
        def fstring(a):
            return f"{a}"
        (pyvm, rvm) = self.function_helper(fstring)
        self.assertEqual(pyvm("abcd"), rvm("abcd"))
