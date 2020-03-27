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
