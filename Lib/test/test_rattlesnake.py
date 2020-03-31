import unittest
from test import support

from rattlesnake.converter import InstructionSetConverter
from rattlesnake import instructions, opcodes, util


class InstructionTest(unittest.TestCase):
    def test_nop(self):
        nop = instructions.NOPInstruction(opcodes.ISET.opmap['NOP'])
        self.assertEqual(nop.opargs, (0,))

    def test_src_dst(self):
        lfr = opcodes.ISET.opmap['LOAD_FAST_REG']
        load = instructions.LoadFastInstruction(lfr, (1, 2))
        self.assertEqual(load.first(), ())
        self.assertEqual(load.dest_registers(), (1,))
        self.assertEqual(load.source_registers(), (2,))
        self.assertEqual(load.rest(), ())
        load.update_opargs(source=(3,))
        self.assertEqual(load.opargs, (1, 3))

    def test_trivial_function(self):
        isc = InstructionSetConverter(_trivial_func.__code__)
        isc.find_blocks()
        isc.convert_address_to_block()
        self.assertEqual(len(isc.blocks), 1)
        self.assertEqual(isc.blocks[0].codelen(), 8)
        isc.gen_rvm()
        self.assertEqual(_get_opcodes(isc.rvm_blocks),
                         [
                             [130, 128, 122, 127],
                         ])
        self.assertEqual(len(isc.rvm_blocks), 1)
        self.assertEqual(isc.rvm_blocks[0].codelen(), 16)
        isc.forward_propagate_fast_loads()
        isc.backward_propagate_fast_stores()
        isc.delete_nops()
        self.assertEqual(isc.rvm_blocks[0].codelen(), 12)
        self.assertEqual(_get_opcodes(isc.rvm_blocks),
                         [
                             [128, 122, 127],
                         ])
        # self.assertEqual(bytes(isc), b'l\x02\x80\x01l\x01l\x02z\x00\x7f\x01')

    def test_simple_branch_function(self):
        isc = InstructionSetConverter(_branch_func.__code__)
        isc.find_blocks()
        isc.convert_address_to_block()
        self.assertEqual(len(isc.blocks), 2)
        self.assertEqual(isc.blocks[0].codelen(), 12)
        self.assertEqual(isc.blocks[1].codelen(), 12)
        self.assertEqual(isc.rvm_blocks, [])
        isc.gen_rvm()
        self.assertEqual(len(isc.rvm_blocks), 2)
        self.assertEqual(isc.rvm_blocks[0].codelen(), 26)
        self.assertEqual(isc.rvm_blocks[1].codelen(), 24)
        self.assertEqual(_get_opcodes(isc.rvm_blocks),
                         [
                             [130, 128, 132, 133, 130, 127],
                             [130, 128, 122, 131, 130, 127],
                         ])

        isc.forward_propagate_fast_loads()
        self.assertEqual(_get_opcodes(isc.rvm_blocks),
                         [
                             [6, 128, 132, 133, 6, 127],
                             [6, 128, 122, 131, 6, 127],
                         ])
        isc.delete_nops()
        self.assertEqual(_get_opcodes(isc.rvm_blocks),
                         [
                             [128, 132, 133, 127],
                             [128, 122, 131, 127],
                         ])
        isc.backward_propagate_fast_stores()
        isc.delete_nops()
        self.assertEqual(_get_opcodes(isc.rvm_blocks),
                         [
                             [128, 132, 133, 127],
                             [128, 122, 127],
                         ])
        # self.assertEqual(bytes(isc), (b'l\x03\x80\x01l\x02l\x00l\x03'
        #                               b'\x84\x04l\x12\x85\x02\x7f\x02'
        #                               b'l\x03\x80\x01l\x01l\x03z\x00\x7f\x02'))

    def test_long_block_function(self):
        isc = InstructionSetConverter(_long_block.__code__)
        isc.find_blocks()
        isc.convert_address_to_block()
        isc.gen_rvm()
        isc.forward_propagate_fast_loads()
        isc.backward_propagate_fast_stores()
        isc.delete_nops()
        opcodes = _get_opcodes(isc.rvm_blocks)
        isc.display_blocks(isc.rvm_blocks)
        self.assertEqual(opcodes[0][:3], [132, 108, 133])

    def test_util_decode(self):
        self.assertEqual(util.decode_oparg(71682), (1, 24, 2))
        self.assertEqual(util.decode_oparg(71682, False), (0, 1, 24, 2))

    def test_util_encode(self):
        self.assertEqual(util.encode_oparg((1, 24, 2)), 71682)

    def test_util_LineNumberDict(self):
        lno_dict = util.LineNumberDict(_get_opcodes.__code__)
        first_lineno = _get_opcodes.__code__.co_firstlineno
        self.assertEqual(lno_dict[26], 4 + first_lineno)
        self.assertEqual(lno_dict[0], 1 + first_lineno)
        self.assertEqual(lno_dict[80], 6 + first_lineno)
        with self.assertRaises(KeyError):
            lno_dict[-10]

        lno_dict = util.LineNumberDict(_get_opcodes.__code__, maxkey=75)
        with self.assertRaises(KeyError):
            lno_dict[80]


def _branch_func(a):
    if a > 4:
        return a
    b = a + 4
    return b

def _trivial_func(a):
    return a + 4

def _get_opcodes(blocks):
    ops = []
    for block in blocks:
        ops.append([])
        for inst in block:
            ops[-1].append(inst.opcode)
    return ops

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
