
import unittest

from rattlesnake.converter import InstructionSetConverter

from . import InstructionTest

class BlockTest(InstructionTest):
    def test_simple_for(self):
        def for_():
            a = -1
            for i in (1, 2):
                a += i
            return a
        (pyvm, rvm) = self.function_helper(for_)
        self.assertEqual(pyvm(), rvm())

    def test_while1(self):
        def while1():
            while True:
                break
        (pyvm, rvm) = self.function_helper(while1)
        self.assertEqual(pyvm(), rvm())

    def test_while2(self):
        def while2(a):
            while a >= 0:
                a -= 1
            return a
        (pyvm, rvm) = self.function_helper(while2)
        self.assertEqual(pyvm(12.1), rvm(12.1))

    def test_while3(self):
        def while3():
            while True:
                pass
        # see bpo40315. Just translating successfully is a win here.
        (pyvm, rvm) = self.function_helper(while3)
