#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

def import_name(self, instr, block):
    op = instr.opcode
    name = instr.opargs[0]
    src = self.pop()
    level = self.top()
    dst = self.top()
    return ImportNameInstruction(opcode.opmap['IMPORT_NAME_REG'], block,
                                 dest=dst, name1=name, source1=src,
                                 level=level)
DISPATCH[opcode.opmap['IMPORT_NAME']] = import_name

# def misc_convert(self, instr, block):
#     op = instr.opcode
#     # if op == opcode.opmap['IMPORT_NAME']:
#     #     dst = self.push()
#     #     return Instruction(opcode.opmap['IMPORT_NAME_REG'], block,
#     #                        (dst, oparg[0]))
#     # opname = "%s_REG" % opcode.opname[op]
#     # if op == opcode.opmap['PRINT_EXPR']:
#     #     src = self.pop()
#     #     return Instruction(opcode.opmap[opname], block, (src,))
# #DISPATCH[opcode.opmap['PRINT_EXPR']] = misc_convert

class ImportNameInstruction(Instruction):
    "dst <- global name"
    def __init__(self, op, block, **kwargs):
        self.populate(("dest", "level", "source1", "name1"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dest, self.level, self.source1, self.name1)
