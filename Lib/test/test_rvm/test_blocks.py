
import opcode
import unittest

from rvm.converter import InstructionSetConverter
from rvm import util

from . import InstructionTest, get_opcodes

_A_GLOBAL = 42

class BlockTest(InstructionTest):
    def test_short_block(self):
        def add(a, b):
            return a + b
        pyvm_code = add.__code__
        isc = InstructionSetConverter(pyvm_code)
        isc.gen_rvm()
        self.assertEqual(len(isc.blocks["PyVM"]), 1)
        self.assertEqual(isc.blocks["PyVM"][0].codelen(), 4)
        self.assertEqual(len(isc.blocks["RVM"]), 1)
        self.assertEqual(get_opcodes(isc.blocks["RVM"]),
                         [
                             [
                                 opcode.opmap["LOAD_FAST_REG"],
                                 opcode.opmap["LOAD_FAST_REG"],
                                 opcode.opmap["BINARY_ADD_REG"],
                                 opcode.opmap["RETURN_VALUE_REG"],
                             ]
                         ])
        self.assertEqual(isc.blocks["RVM"][0].codelen(), 8)
        isc.forward_propagate_fast_loads()
        isc.delete_nops()
        self.assertEqual(isc.blocks["RVM"][0].codelen(), 4)
        self.assertEqual(get_opcodes(isc.blocks["RVM"]),
                         [
                             [
                                 opcode.opmap["BINARY_ADD_REG"],
                                 opcode.opmap["RETURN_VALUE_REG"],
                             ]
                         ])

    def test_long_block(self):
        def long_block(s, b):
            global _A_GLOBAL
            _A_GLOBAL = 42
            if s > b:
                _A_GLOBAL += 1
                s = b - 21
                b = s * 44
                s = b + 4
                b = s - 21
                s = b + False
                b = s + 24
                s = b - 21
                b = s * 44
                s = b + 4
                b = s - 21
                s = b + _A_GLOBAL
                b = s + 24
                s = b - True
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
            _A_GLOBAL -= 1
            return b - 1
        (pyvm, rvm) = self.function_helper(long_block, propagate=False)
        self.assertEqual(pyvm(7, 3), rvm(7, 3))
        self.assertEqual(pyvm(3, 7), rvm(3, 7))

    def test_util_LineNumberDict(self):
        lno_dict = util.LineNumberDict(get_opcodes.__code__)
        first_lineno = get_opcodes.__code__.co_firstlineno
        self.assertEqual(lno_dict[26], 4 + first_lineno)
        self.assertEqual(lno_dict[0], 1 + first_lineno)
        self.assertEqual(lno_dict[80], 6 + first_lineno)
        with self.assertRaises(KeyError):
            _x = lno_dict[-10]
        lno_dict = util.LineNumberDict(get_opcodes.__code__, maxkey=75)
        with self.assertRaises(KeyError):
            _x = lno_dict[80]

    def test_util_decode(self):
        self.assertEqual(util.decode_oparg(0), (0,))
        self.assertEqual(util.decode_oparg(71682), (1, 24, 2))
        self.assertEqual(util.decode_oparg(71682, False), (0, 1, 24, 2))

    def test_util_encode(self):
        self.assertEqual(util.encode_oparg((1, 24, 2)), 71682)
        self.assertEqual(util.encode_oparg(()), 0)

    def test_set_global(self):
        def set_global():
            global _A_GLOBAL
            _A_GLOBAL = 42
            return _A_GLOBAL
        (pyvm, rvm) = self.function_helper(set_global)
        self.assertEqual(pyvm(), rvm())
