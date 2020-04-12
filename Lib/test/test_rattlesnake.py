"RVM tests"

import dis
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
        pyvm_code = _add.__code__
        isc = InstructionSetConverter(pyvm_code)
        isc.gen_rvm()
        self.assertEqual(len(isc.blocks["PyVM"]), 1)
        self.assertEqual(isc.blocks["PyVM"][0].codelen(), 8)
        self.assertEqual(len(isc.blocks["RVM"]), 1)
        self.assertEqual(_get_opcodes(isc.blocks["RVM"]),
                         [
                             [130, 130, 122, 127],
                         ])
        self.assertEqual(isc.blocks["RVM"][0].codelen(), 16)
        isc.forward_propagate_fast_loads()
        isc.backward_propagate_fast_stores()
        isc.delete_nops()
        self.assertEqual(isc.blocks["RVM"][0].codelen(), 8)
        self.assertEqual(_get_opcodes(isc.blocks["RVM"]),
                         [
                             [122, 127],
                         ])

    def test_product(self):
        (pyvm, rvm) = self.function_helper(_product)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

    def test_true_divide(self):
        (pyvm, rvm) = self.function_helper(_true_divide)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

    def test_floor_divide(self):
        (pyvm, rvm) = self.function_helper(_floor_divide)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

    def test_subtract(self):
        (pyvm, rvm) = self.function_helper(_subtract)
        self.assertEqual(pyvm(5, 9.0), rvm(5, 9.0))

    def test_subscript(self):
        (pyvm, rvm) = self.function_helper(_subscript)
        for (container, index) in (
                (dict(zip("abcdefghij", range(10))), "h"),
                (dict(zip(range(10), "abcdefghij")), 4),
                ("abc", 2)
                ):
            self.assertEqual(pyvm(container, index),
                             rvm(container, index))

    def test_tuple(self):
        (pyvm, rvm) = self.function_helper(_tuple)
        self.assertEqual(pyvm(1, 2, 3), rvm(1, 2, 3))

    def test_list(self):
        (pyvm, rvm) = self.function_helper(_list)
        self.assertEqual(pyvm(), rvm())

    def test_power(self):
        (pyvm, rvm) = self.function_helper(_power)
        self.assertEqual(pyvm(5.0, 7), rvm(5.0, 7))

    def test_add(self):
        (pyvm, rvm) = self.function_helper(_add)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))
        self.assertEqual(pyvm("xyz", "abc"), rvm("xyz", "abc"))

    def test_modulo(self):
        (pyvm, rvm) = self.function_helper(_modulo)
        self.assertEqual(pyvm(5, 2), rvm(5, 2))
        self.assertEqual(pyvm("%s", 47), rvm("%s", 47))

    def test_not(self):
        (pyvm, rvm) = self.function_helper(_not)
        self.assertEqual(rvm(5), False)
        self.assertEqual(rvm(None), True)

    def test_simple_branch_function(self):
        (pyvm, rvm) = self.function_helper(_branch_func)
        self.assertEqual(pyvm(7), rvm(7))

    def test_jump_if_false(self):
        (pyvm, rvm) = self.function_helper(_jump_if_false)
        self.assertEqual(pyvm(7), rvm(7))
        self.assertEqual(pyvm(0), rvm(0))
        self.assertEqual(pyvm(()), rvm(()))
        self.assertEqual(pyvm(False), rvm(False))
        self.assertEqual(pyvm(True), rvm(True))

    def test_jump_if_true(self):
        (pyvm, rvm) = self.function_helper(_jump_if_true)
        self.assertEqual(pyvm(7), rvm(7))
        self.assertEqual(pyvm(0), rvm(0))
        self.assertEqual(pyvm(()), rvm(()))
        self.assertEqual(pyvm(False), rvm(False))
        self.assertEqual(pyvm(True), rvm(True))

    def test_long_block_function(self):
        for prop in (True, False):
            (pyvm, rvm) = self.function_helper(_long_block, propagate=prop)
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

    def function_helper(self, func, propagate=True, verbose=False):
        pyvm_code = func.__code__
        isc = InstructionSetConverter(pyvm_code)
        isc.gen_rvm()
        if propagate:
            isc.forward_propagate_fast_loads()
            isc.backward_propagate_fast_stores()
            isc.delete_nops()

        # Lacking a proper API at this point...
        def rvm(a): return a
        rvm_replace_code(rvm, pyvm_code, isc)

        # just for symmetry with construction of rvm...
        def pyvm(a): return a
        pyvm.__code__ = pyvm_code

        self.assertEqual(pyvm.__code__.co_flags & util.CO_REGISTER, 0)
        self.assertEqual(rvm.__code__.co_flags & util.CO_REGISTER,
                         util.CO_REGISTER)

        if verbose:
            print()
            dis.dis(pyvm)
            print()
            dis.dis(rvm)
        return (pyvm, rvm)

def _branch_func(a):
    if a > 4:
        return a
    b = a + 4
    return b

def _tuple(a, b, c):
    return (a, b, c)

def _list():
    return ['a', 'b', 'c']

def _not(val):
    return not val

def _true_divide(a, b):
    return a / b

def _floor_divide(a, b):
    return a // b

def _product(a, b):
    return a * b

def _power(base, exp):
    return base ** exp

def _modulo(a, b):
    return a % b

def _add(a, b):
    return a + b

def _subtract(a, b):
    return a - b

def _subscript(container, index):
    return container[index]

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

def _jump_if_true(a):
    if not a:
        return 42
    return 42

def _jump_if_false(a):
    if a:
        return 42
    return 42

_A_GLOBAL = 42
def _long_block(s, b):
    if s > b:
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
    return b - 1

def rvm_replace_code(func, pyvm_code, isc):
    "Modify func using PyVM bits from pyvm_code & RVM bits from."
    rvm_flags = pyvm_code.co_flags | util.CO_REGISTER
    rvm_code = pyvm_code.replace(co_code=bytes(isc),
                                 co_lnotab=isc.get_lnotab(),
                                 co_flags=rvm_flags)
    func.__code__ = rvm_code
