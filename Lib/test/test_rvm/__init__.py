"RVM Tests"

import dis
import opcode
import os
import sys
from test.support import load_package_tests
import unittest

from rattlesnake.converter import InstructionSetConverter
from rattlesnake import instructions, util
from rattlesnake.loadstore import LoadFastInstruction


instructions.Instruction.dump_at_end = False

class InstructionTest(unittest.TestCase):
    def function_helper(self, func, propagate=True, verbose=False):
        pyvm_code = func.__code__

        # just for symmetry with construction of rvm below...
        def pyvm(*args):
            return args
        pyvm.__code__ = pyvm_code
        if verbose:
            print(file=sys.stderr)
            dis.dis(pyvm, file=sys.stderr)

        isc = InstructionSetConverter(pyvm_code)
        isc.gen_rvm()
        if propagate:
            isc.forward_propagate_fast_loads()
            isc.delete_nops()

        if verbose:
            print(file=sys.stderr)
            isc.display_blocks(isc.blocks["RVM"])

        # Lacking a proper API at this point...
        def rvm(*args):
            return args
        rvm_replace_code(rvm, pyvm_code, isc)

        self.assertEqual(pyvm.__code__.co_flags & util.CO_REGISTER, 0)
        self.assertEqual(rvm.__code__.co_flags & util.CO_REGISTER,
                         util.CO_REGISTER)

        if verbose:
            print(file=sys.stderr)
            dis.dis(rvm, file=sys.stderr)
        return (pyvm, rvm)

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

# HELPERS:

def get_opcodes(blocks):
    ops = []
    for block in blocks:
        ops.append([])
        for inst in block:
            ops[-1].append(inst.opcode)
    return ops

def rvm_replace_code(func, pyvm_code, isc):
    "Modify func using PyVM bits from pyvm_code & RVM bits from."
    rvm_flags = pyvm_code.co_flags | util.CO_REGISTER
    rvm_code = pyvm_code.replace(co_code=bytes(isc),
                                 co_linetable=isc.get_lnotab(),
                                 co_flags=rvm_flags)
    func.__code__ = rvm_code

def load_tests(*args):
    return load_package_tests(os.path.dirname(__file__), *args)
