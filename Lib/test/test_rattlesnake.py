"RVM tests"

import dis
import opcode
import unittest

from rattlesnake.converter import InstructionSetConverter
from rattlesnake import instructions, util
from rattlesnake.loadstore import LoadFastInstruction

instructions.Instruction.dump_at_end = True

_A_GLOBAL = 42

# When referencing issues in the issue tracker, name them rsNNNN,
# where NNNN is the issue number with leading zeroes.

class InstructionTest(unittest.TestCase):
    def test_add(self):
        def add(a, b):
            return a + b
        (pyvm, rvm) = self.function_helper(add)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))
        self.assertEqual(pyvm("xyz", "abc"), rvm("xyz", "abc"))

    def test_and(self):
        def and_(a, b):
            return a & b
        (pyvm, rvm) = self.function_helper(and_)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))

    def test_blocks(self):
        def add(a, b):
            return a + b
        pyvm_code = add.__code__
        isc = InstructionSetConverter(pyvm_code)
        isc.gen_rvm()
        self.assertEqual(len(isc.blocks["PyVM"]), 1)
        self.assertEqual(isc.blocks["PyVM"][0].codelen(), 8)
        self.assertEqual(len(isc.blocks["RVM"]), 1)
        self.assertEqual(get_opcodes(isc.blocks["RVM"]),
                         [
                             [136, 136, 119, 133],
                         ])
        self.assertEqual(isc.blocks["RVM"][0].codelen(), 16)
        isc.forward_propagate_fast_loads()
        isc.delete_nops()
        self.assertEqual(isc.blocks["RVM"][0].codelen(), 8)
        self.assertEqual(get_opcodes(isc.blocks["RVM"]),
                         [
                             [119, 133],
                         ])

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

    def test_callfunc(self):
        def callfunc():
            return [bin(2796202), list(enumerate("1234", 2))]
        (pyvm, rvm) = self.function_helper(callfunc)
        self.assertEqual(pyvm(), rvm())

    def test_callfunc_kw(self):
        (pyvm, rvm) = self.function_helper(_callfunc_kw)
        self.assertEqual(pyvm(), rvm())

    def test_callfunc_protected_reg(self):
        (pyvm, rvm) = self.function_helper(_callfunc_protected_reg)
        self.assertEqual(pyvm(13.0), rvm(13.0))

    def test_floor_divide(self):
        def floor_divide(a, b):
            return a // b
        (pyvm, rvm) = self.function_helper(floor_divide)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

    def test_inplace_add(self):
        def inplace_add(a, b):
            a += b
            return a
        (pyvm, rvm) = self.function_helper(inplace_add)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_and(self):
        def inplace_and(a, b):
            a &= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_and)
        self.assertEqual(pyvm(5, 99), rvm(5, 99))

    def test_inplace_floor_divide(self):
        def inplace_floor_divide(a, b):
            a //= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_floor_divide)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))
        self.assertEqual(pyvm(9, 5), rvm(9, 5))

    def test_inplace_lshift(self):
        def inplace_lshift(a, b):
            a <<= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_lshift)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_mod(self):
        def inplace_mod(a, b):
            a %= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_mod)
        self.assertEqual(pyvm(15, 9), rvm(15, 9))

    def test_inplace_mul(self):
        def inplace_mul(a, b):
            a *= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_mul)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_or(self):
        def inplace_or(a, b):
            a |= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_or)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_pow(self):
        def inplace_pow(a, b):
            a **= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_pow)
        self.assertEqual(pyvm(5, 9.1), rvm(5, 9.1))

    def test_inplace_rshift(self):
        def inplace_rshift(a, b):
            a >>= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_rshift)
        self.assertEqual(pyvm(5 ** 9, 4), rvm(5 ** 9, 4))

    def test_inplace_subtract(self):
        def inplace_subtract(a, b):
            a -= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_subtract)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_inplace_true_divide(self):
        def inplace_true_divide(a, b):
            a /= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_true_divide)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))
        self.assertEqual(pyvm(9.0, 4), rvm(9.0, 4))

    def test_inplace_xor(self):
        def inplace_xor(a, b):
            a ^= b
            return a
        (pyvm, rvm) = self.function_helper(inplace_xor)
        self.assertEqual(pyvm(5, 9), rvm(5, 9))

    def test_invert(self):
        def invert(val):
            return ~val
        (pyvm, rvm) = self.function_helper(invert)
        for val in (5, -99):
            self.assertEqual(pyvm(val), rvm(val))

    def test_jump_if_false(self):
        def jump_if_false(a):
            if a:
                return 42
            return 41
        (pyvm, rvm) = self.function_helper(jump_if_false)
        self.assertEqual(pyvm(7), rvm(7))
        self.assertEqual(pyvm(0), rvm(0))
        self.assertEqual(pyvm(()), rvm(()))
        self.assertEqual(pyvm(False), rvm(False))
        self.assertEqual(pyvm(True), rvm(True))

    def test_jump_if_true(self):
        def jump_if_true(a):
            if not a:
                return 42
            return 43
        (pyvm, rvm) = self.function_helper(jump_if_true)
        self.assertEqual(pyvm(7), rvm(7))
        self.assertEqual(pyvm(0), rvm(0))
        self.assertEqual(pyvm(()), rvm(()))
        self.assertEqual(pyvm(False), rvm(False))
        self.assertEqual(pyvm(True), rvm(True))

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

    def test_long_block_function(self):
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
        for prop in (True, False):
            (pyvm, rvm) = self.function_helper(long_block, propagate=prop)
            self.assertEqual(pyvm(7, 3), rvm(7, 3))
            self.assertEqual(pyvm(3, 7), rvm(3, 7))

    def test_lshift(self):
        def lshift(a, b):
            return a << b
        (pyvm, rvm) = self.function_helper(lshift)
        self.assertEqual(pyvm(70, 5), rvm(70, 5))

    def test_modulo(self):
        def modulo(a, b):
            return a % b
        (pyvm, rvm) = self.function_helper(modulo)
        self.assertEqual(pyvm(5, 2), rvm(5, 2))
        self.assertEqual(pyvm("%s", 47), rvm("%s", 47))

    def test_negative(self):
        def negative(val):
            return -val
        (pyvm, rvm) = self.function_helper(negative)
        for val in (5, -99):
            self.assertEqual(pyvm(val), rvm(val))

    def test_nop(self):
        nop = instructions.NOPInstruction(opcode.opmap['NOP'], 0)
        self.assertEqual(nop.opargs, (0,))

    def test_not(self):
        def not_(val):
            return not val
        (pyvm, rvm) = self.function_helper(not_)
        for val in (5, None, ()):
            self.assertEqual(pyvm(val), rvm(val))

    def test_or(self):
        def or_(a, b):
            return a | b
        (pyvm, rvm) = self.function_helper(or_)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))

    def test_positive(self):
        def positive(val):
            return +val
        (pyvm, rvm) = self.function_helper(positive)
        for val in (5, -99):
            self.assertEqual(pyvm(val), rvm(val))

    def test_power(self):
        def power(base, exp):
            return base ** exp
        (pyvm, rvm) = self.function_helper(power)
        self.assertEqual(pyvm(5.0, 7), rvm(5.0, 7))

    def test_product(self):
        def product(a, b):
            return a * b
        (pyvm, rvm) = self.function_helper(product)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

    # def test_rs0009(self):
    #     def load_store():
    #         a = 7
    #         b = a
    #         return a + b
    #     (pyvm, rvm) = self.function_helper(load_store)
    #     self.assertEqual(pyvm(), rvm())

    def test_rshift(self):
        def rshift(a, b):
            return a >> b
        (pyvm, rvm) = self.function_helper(rshift)
        self.assertEqual(pyvm(79999, 3), rvm(79999, 3))

    def test_set_global(self):
        def set_global():
            global _A_GLOBAL
            _A_GLOBAL = 42
            return _A_GLOBAL
        (pyvm, rvm) = self.function_helper(set_global)
        self.assertEqual(pyvm(), rvm())

    def test_simple_branch_function(self):
        def branch_func(a):
            if a > 4:
                return a
            if a in (1, 2):
                return a
            b = a + 4
            return b
        (pyvm, rvm) = self.function_helper(branch_func)
        self.assertEqual(pyvm(7), rvm(7))
        self.assertEqual(pyvm(1), rvm(1))
        self.assertEqual(pyvm(0), rvm(0))

    def test_simple_for(self):
        def for_():
            a = -1
            for i in (1, 2):
                a += i
            return a
        (pyvm, rvm) = self.function_helper(for_)
        self.assertEqual(pyvm(), rvm())

    # def test_simple_yield(self):
    #     def yield_value(a):
    #         yield a
    #     (pyvm, rvm) = self.function_helper(yield_value)
    #     self.assertEqual(list(pyvm(42)), list(rvm(42)))

    # def test_simple_import(self):
    #     def import_name():
    #         import sys
    #         return sys
    #     (pyvm, rvm) = self.function_helper(import_name)
    #     self.assertEqual(pyvm(), rvm())

    def test_src_dst(self):
        lfr = opcode.opmap['LOAD_FAST_REG']
        load = LoadFastInstruction(lfr, 0, dest=1, source1=2)
        self.assertEqual(load.source1, 2)
        self.assertEqual(load.dest, 1)
        load.source1 = 3
        self.assertEqual(load.opargs, (1, 3))

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

    def test_subtract(self):
        def subtract(a, b):
            return a - b
        (pyvm, rvm) = self.function_helper(subtract)
        self.assertEqual(pyvm(5, 9.0), rvm(5, 9.0))

    def test_true_divide(self):
        def true_divide(a, b):
            return a / b
        (pyvm, rvm) = self.function_helper(true_divide)
        self.assertEqual(pyvm(1, 5), rvm(1, 5))
        self.assertEqual(pyvm(5, 1), rvm(5, 1))

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

    def test_xor(self):
        def xor(a, b):
            return a ^ b
        (pyvm, rvm) = self.function_helper(xor)
        self.assertEqual(pyvm(5, 70), rvm(5, 70))

    def function_helper(self, func, propagate=True, verbose=False):
        pyvm_code = func.__code__

        # just for symmetry with construction of rvm below...
        def pyvm(a): return a
        pyvm.__code__ = pyvm_code
        if verbose:
            print()
            dis.dis(pyvm)

        isc = InstructionSetConverter(pyvm_code)
        isc.gen_rvm()
        if propagate:
            isc.forward_propagate_fast_loads()
            isc.delete_nops()

        if verbose:
            print()
            isc.display_blocks(isc.blocks["RVM"])

        # Lacking a proper API at this point...
        def rvm(a): return a
        rvm_replace_code(rvm, pyvm_code, isc)

        self.assertEqual(pyvm.__code__.co_flags & util.CO_REGISTER, 0)
        self.assertEqual(rvm.__code__.co_flags & util.CO_REGISTER,
                         util.CO_REGISTER)

        if verbose:
            print()
            dis.dis(rvm)
        return (pyvm, rvm)

# Still required to be at top level for now...
def _test_cf(a, b, c):
    return a + b + c

def _callfunc_protected_reg(a):
    return _test_cf(a, a ** 2, a / 7)

def _kw_func(a, b=None):
    return (a, b)

def _callfunc_kw():
    return _kw_func(14, b="hello world")

# STILL TO DO:

def _inplace_matmul(a, b):
    a @= b
    return a

def _build_slice(*args):
    keys = args[::2]
    vals = args[1::2]
    dct = dict(zip(keys, vals))
    return dct

# ... and many more ...

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
                                 co_lnotab=isc.get_lnotab(),
                                 co_flags=rvm_flags)
    func.__code__ = rvm_code
