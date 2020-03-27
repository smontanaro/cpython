import unittest
from test import support

from rattlesnake.converter import InstructionSetConverter
from rattlesnake import instructions, opcodes

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

    def test_simple_function(self):
        def func(a):
            return a + 4
        isc = InstructionSetConverter(func.__code__)
        isc.find_blocks()
        isc.convert_address_to_block()
        self.assertEqual(len(isc.blocks), 1)
        self.assertEqual(isc.blocks[0].codelen(), 8)
        isc.gen_rvm()
        self.assertEqual(len(isc.rvm_blocks), 1)
        self.assertEqual(isc.rvm_blocks[0].codelen(), 16)
        isc.forward_propagate_fast_reads()
        isc.delete_nops()
        self.assertEqual(isc.rvm_blocks[0].codelen(), 12)

    def test_branch_function(self):
        def func(a):
            if a > 4:
                return a
            b = a + 4
            return b

        def count_nops(block):
            return len([i for i in block
                            if isinstance(i, instructions.NOPInstruction)])

        isc = InstructionSetConverter(func.__code__)
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

        isc.forward_propagate_fast_reads()

        counts = []
        for block in isc.rvm_blocks:
            counts.append(count_nops(block))
        self.assertEqual(sum(counts), 4)

        isc.delete_nops()

        counts = []
        for block in isc.rvm_blocks:
            counts.append(count_nops(block))
        self.assertEqual(sum(counts), 0)

        isc.backward_propagate_fast_writes()

        counts = []
        for block in isc.rvm_blocks:
            counts.append(count_nops(block))
        self.assertEqual(sum(counts), 1)

        isc.delete_nops()

        counts = []
        for block in isc.rvm_blocks:
            counts.append(count_nops(block))
        self.assertEqual(sum(counts), 0)
