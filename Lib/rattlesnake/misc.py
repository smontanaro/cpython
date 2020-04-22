#!/usr/bin/env python3

import opcode

from . import DISPATCH
from .instructions import Instruction

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
# #DISPATCH[opcode.opmap['IMPORT_NAME']] = misc_convert
# #DISPATCH[opcode.opmap['PRINT_EXPR']] = misc_convert
