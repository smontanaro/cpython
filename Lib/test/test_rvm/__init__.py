"RVM Tests"

import dis
import opcode
import os
import sys
from test.support import load_package_tests
import unittest

from rvm.converter import InstructionSetConverter
from rvm import instructions, util


instructions.Instruction.dump_at_end = False

class InstructionTest(unittest.TestCase):
    def function_helper(self, func, propagate=False, verbose=False):
        pyvm_code = func.__code__

        # # just for symmetry with construction of rvm below...
        # def pyvm(a):
        #     return args
        # pyvm.__code__ = pyvm_code
        if verbose:
            print(file=sys.stderr)
            dis.dis(func, file=sys.stderr)

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

        self.assertEqual(func.__code__.co_flags & util.CO_REGISTER, 0)
        self.assertEqual(rvm.__code__.co_flags & util.CO_REGISTER,
                         util.CO_REGISTER)

        if verbose:
            print(file=sys.stderr)
            dis.dis(rvm, file=sys.stderr)
        return (func, rvm)

# HELPERS:

def get_opcodes(blocks):
    ops = []
    for block in blocks:
        ops.append([])
        for inst in block:
            ops[-1].append(inst.opcode)
    return ops

def rvm_replace_code(func, pyvm_code, isc):
    "Modify func using PyVM bits from pyvm_code & RVM bits from isc."
    rvm_flags = pyvm_code.co_flags | util.CO_REGISTER
    rvm_code = pyvm_code.replace(co_code=bytes(isc),
                                 co_linetable=isc.get_lnotab(),
                                 co_flags=rvm_flags)
    func.__code__ = rvm_code

def load_tests(*args):
    return load_package_tests(os.path.dirname(__file__), *args)
