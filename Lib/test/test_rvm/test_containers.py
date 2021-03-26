
import dis
import sys
import types
import unittest

from . import InstructionTest

class BlockTest(InstructionTest):
    def test_set(self):
        def set_(x):
            return {'a', x, 'c'}
        (pyvm, rvm) = self.function_helper(set_)
        self.assertEqual(pyvm(42), rvm(42))

    def test_list(self):
        def list_(x):
            return ['a', x, 'c']
        (pyvm, rvm) = self.function_helper(list_)
        self.assertEqual(pyvm(42), rvm(42))

    def test_list_extend(self):
        def listextend():
            return [1, 2, 3]
        (pyvm, rvm) = self.function_helper(listextend)
        self.assertEqual(pyvm(), rvm())

    def test_subscript(self):
        def subscript(container, index):
            return container[index]
        (pyvm, rvm) = self.function_helper(subscript)
        for (container, index) in (
                (dict(zip("abcdefghij", range(10))), "h"),
                (dict(zip(range(10), "abcdefghij")), 4),
                ("abc", 2)
                ):
            self.assertEqual(pyvm(container, index),
                             rvm(container, index))

    def test_tuple(self):
        def tuple_(a, b, c):
            return (a, b, c)
        (pyvm, rvm) = self.function_helper(tuple_)
        self.assertEqual(pyvm(1, 2, 3), rvm(1, 2, 3))

    def test_tuple2(self):
        def tuple2(a):
            return (a, a+1, a+2, a+3)
        (pyvm, rvm) = self.function_helper(tuple2)
        self.assertEqual(pyvm(42), rvm(42))

    @unittest.skip('currently broken')
    def test_dict_merge(self):
        def f(ns_dict):
            ns = types.SimpleNamespace(**ns_dict)
            return ns
        (pyvm, rvm) = self.function_helper(f)
        print("*** stack ***", file=sys.stderr)
        dis.dis(pyvm, file=sys.stderr)
        print("*** register ***", file=sys.stderr)
        dis.dis(rvm, file=sys.stderr)
        ns_dict = {'a': 1}
        self.assertEqual(pyvm(ns_dict), rvm(ns_dict))

    def test_build_dict(self):
        def build_dict(a, b):
            return {a: b}
        (pyvm, rvm) = self.function_helper(build_dict)
        self.assertEqual(pyvm("a", 1), rvm("a", 1))

    def test_build_empty_dict(self):
        def build_empty_dict():
            return {}
        (pyvm, rvm) = self.function_helper(build_empty_dict)
        self.assertEqual(pyvm(), rvm())
