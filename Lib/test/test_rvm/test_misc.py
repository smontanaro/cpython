"""Tests which (so far) don't fit anywhere else."""

import opcode
import unittest

from rvm.loadstore import LoadFastInstruction
from rvm import instructions

from . import InstructionTest

class MiscTest(InstructionTest):
    def test_src_dst(self):
        lfr = opcode.opmap['LOAD_FAST_REG']
        load = LoadFastInstruction(lfr, 0, dest=1, source1=2)
        self.assertEqual(load.source1, 2)
        self.assertEqual(load.dest, 1)
        load.source1 = 3
        self.assertEqual(load.opargs, (1, 3))

    @unittest.skip('currently broken')
    def test_simple_yield(self):
        def yield_value(a):
            yield a
        (pyvm, rvm) = self.function_helper(yield_value)
        self.assertEqual(list(pyvm(42)), list(rvm(42)))

    def test_simple_import(self):
        def import_name():
            # pylint: disable=import-outside-toplevel
            import string
            return string
        (pyvm, rvm) = self.function_helper(import_name)
        self.assertEqual(pyvm(), rvm())

    def test_load_set_del_attr(self):
        def set_del_attr(a):
            a.someattr = 4
            x = a.someattr
            del a.someattr
            return x
        class Klass:
            pass
        (pyvm, rvm) = self.function_helper(set_del_attr)
        self.assertEqual(pyvm(Klass), rvm(Klass))

    def test_nop(self):
        nop = instructions.NOPInstruction(opcode.opmap['NOP'], 0)
        self.assertEqual(nop.opargs, (0,))

    def test_rs0009(self):
        def load_store():
            a = 7
            b = a
            return a + b
        (pyvm, rvm) = self.function_helper(load_store)
        self.assertEqual(pyvm(), rvm())
