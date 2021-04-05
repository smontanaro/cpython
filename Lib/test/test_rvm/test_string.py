
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

    def test_fstring_simple(self):
        def fstring(a):
            return f"{a}"
        (pyvm, rvm) = self.function_helper(fstring)
        self.assertEqual(pyvm("abcd"), rvm("abcd"))

    def test_fstring_converter(self):
        def fstring(a):
            return f"{a!a}"
        (pyvm, rvm) = self.function_helper(fstring)
        self.assertEqual(pyvm("bcd"), rvm("bcd"))

    def test_fstring_number(self):
        def fstring(a):
            return f"{a:.3g}"
        (pyvm, rvm) = self.function_helper(fstring)
        self.assertEqual(pyvm(10.7766e7), rvm(10.7766e7))
