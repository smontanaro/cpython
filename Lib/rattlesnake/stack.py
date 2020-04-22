#!/usr/bin/env python3

import opcode

from rattlesnake import DISPATCH
from rattlesnake.instructions import Instruction

# def stack_convert(self, instr, block):
#     op = instr.opcode
#     if op == opcode.opmap['POP_TOP']:
#         self.pop()
#         return NOPInstruction(self.NOP_OPCODE, block)
#     if op == opcode.opmap['DUP_TOP']:
#         # nop
#         _dummy = self.top()
#         _dummy = self.push()
#         return NOPInstruction(self.NOP_OPCODE, block)
#     if op == opcode.opmap['ROT_TWO']:
#         return Instruction(opcode.opmap['ROT_TWO_REG'], block,
#                            (self.top(),))
#     if op == opcode.opmap['ROT_THREE']:
#         return Instruction(opcode.opmap['ROT_THREE_REG'], block,
#                            (self.top(),))
#     if op == opcode.opmap['POP_BLOCK']:
#         return Instruction(opcode.opmap['POP_BLOCK_REG'], block)
#     raise ValueError(f"Unhandled opcode {opcode.opname[op]}")
# DISPATCH[opcode.opmap['POP_TOP']] = stack_convert
# DISPATCH[opcode.opmap['ROT_TWO']] = stack_convert
# DISPATCH[opcode.opmap['ROT_THREE']] = stack_convert
# DISPATCH[opcode.opmap['DUP_TOP']] = stack_convert
# DISPATCH[opcode.opmap['POP_BLOCK']] = stack_convert
