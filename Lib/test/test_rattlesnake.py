"RVM tests"

import unittest

from rattlesnake.converter import InstructionSetConverter
from rattlesnake import instructions, opcodes, util


class InstructionTest(unittest.TestCase):
    def test_nop(self):
        nop = instructions.NOPInstruction(opcodes.ISET.opmap['NOP'], 0)
        self.assertEqual(nop.opargs, (0,))

    def test_src_dst(self):
        lfr = opcodes.ISET.opmap['LOAD_FAST_REG']
        load = instructions.LoadFastInstruction(lfr, 0, dest=1, source1=2)
        self.assertEqual(load.source1, 2)
        self.assertEqual(load.dest, 1)
        load.source1 = 3
        self.assertEqual(load.opargs, (1, 3))

    def test_blocks(self):
        pyvm_code = _trivial_func.__code__
        isc = InstructionSetConverter(pyvm_code)
        isc.gen_rvm()
        self.assertEqual(len(isc.blocks["PyVM"]), 1)
        self.assertEqual(isc.blocks["PyVM"][0].codelen(), 8)
        self.assertEqual(len(isc.blocks["RVM"]), 1)
        self.assertEqual(_get_opcodes(isc.blocks["RVM"]),
                         [
                             [130, 128, 123, 127],
                         ])
        self.assertEqual(isc.blocks["RVM"][0].codelen(), 16)
        isc.forward_propagate_fast_loads()
        isc.backward_propagate_fast_stores()
        isc.delete_nops()
        self.assertEqual(isc.blocks["RVM"][0].codelen(), 12)
        self.assertEqual(_get_opcodes(isc.blocks["RVM"]),
                         [
                             [128, 123, 127],
                         ])

    def test_trivial_function(self):
        (pyvm, rvm) = self._function_helper(_trivial_func)
        self.assertEqual(pyvm(5), rvm(5))

    def test_trivial_str_function(self):
        (pyvm, rvm) = self._function_helper(_trivial_str_func)
        self.assertEqual(pyvm("xyz"), rvm("xyz"))

    def test_simple_branch_function(self):
        (pyvm, rvm) = self._function_helper(_branch_func)
        self.assertEqual(pyvm(7), rvm(7))

    def test_long_block_function(self):
        (pyvm, rvm) = self._function_helper(_long_block)
        self.assertEqual(pyvm(7, 3), rvm(7, 3))
        self.assertEqual(pyvm(3, 7), rvm(3, 7))

    def test_util_decode(self):
        self.assertEqual(util.decode_oparg(0), (0,))
        self.assertEqual(util.decode_oparg(71682), (1, 24, 2))
        self.assertEqual(util.decode_oparg(71682, False), (0, 1, 24, 2))

    def test_util_encode(self):
        self.assertEqual(util.encode_oparg((1, 24, 2)), 71682)
        self.assertEqual(util.encode_oparg(()), 0)

    def test_util_LineNumberDict(self):
        lno_dict = util.LineNumberDict(_get_opcodes.__code__)
        first_lineno = _get_opcodes.__code__.co_firstlineno
        self.assertEqual(lno_dict[26], 4 + first_lineno)
        self.assertEqual(lno_dict[0], 1 + first_lineno)
        self.assertEqual(lno_dict[80], 6 + first_lineno)
        with self.assertRaises(KeyError):
            _x = lno_dict[-10]

        lno_dict = util.LineNumberDict(_get_opcodes.__code__, maxkey=75)
        with self.assertRaises(KeyError):
            _x = lno_dict[80]

    def _function_helper(self, func):
        pyvm_code = func.__code__
        isc = InstructionSetConverter(pyvm_code)
        isc.gen_rvm()
        isc.forward_propagate_fast_loads()
        isc.backward_propagate_fast_stores()
        isc.delete_nops()

        # Lacking a proper API at this point...
        def rvm(a): return a
        _rvm_replace_code(rvm, pyvm_code, isc)

        # just for symmetry with construction of rvm...
        def pyvm(a): return a
        pyvm.__code__ = pyvm_code

        self.assertEqual(pyvm.__code__.co_flags & util.CO_REGISTER, 0)
        self.assertEqual(rvm.__code__.co_flags & util.CO_REGISTER,
                         util.CO_REGISTER)

        return (pyvm, rvm)

def _branch_func(a):
    if a > 4:
        return a
    b = a + 4
    return b

def _trivial_func(a):
    return a - 4

def _trivial_str_func(a):
    return a + "abc"

def _get_opcodes(blocks):
    ops = []
    for block in blocks:
        ops.append([])
        for inst in block:
            ops[-1].append(inst.opcode)
    return ops

def _get_opnames(blocks):
    names = []
    for block in blocks:
        names.append([])
        for inst in block:
            names[-1].append(opcodes.ISET.opname[inst.opcode])
    return names

_A_GLOBAL = 42
def _long_block(s, b):
    if s > b:
        s = b - 21
        b = s * 44
        s = b + 4
        b = s - 21
        s = b + _A_GLOBAL
        b = s + 24
        s = b - 21
        b = s * 44
        s = b + 4
        b = s - 21
        s = b + _A_GLOBAL
        b = s + 24
        s = b - 21
        b = s * 44
        b = s - 21
        s = b + _A_GLOBAL
        b = s + 24
        s = b - 21
        b = s - 21
        s = b + _A_GLOBAL
        b = s + 24
        s = b - 21
        b = s + 24
        s = b - 21
        b = s - 21
        s = b + _A_GLOBAL
        b = s + 24
        s = b - 21
        b = s - 21
        s = b + _A_GLOBAL
        b = s + 24
        s = b - 21
        return s
    return b - 1

def _rvm_replace_code(func, pyvm_code, isc):
    "Modify func using PyVM bits from pyvm_code & RVM bits from."
    rvm_flags = pyvm_code.co_flags | util.CO_REGISTER
    rvm_code = pyvm_code.replace(co_code=bytes(isc),
                                 co_lnotab=isc.get_lnotab(),
                                 co_flags=rvm_flags)
    func.__code__ = rvm_code
