#!/usr/bin/env python3

"DICT_UPDATE & DICT_MERGE"

import opcode

from . import DISPATCH
from .instructions import Instruction

def dict_op(self, instr, block):
    op = instr.opcode
    oparg = instr.opargs[0] # All PyVM opcodes have a single oparg
    opname = "%s_REG" % opcode.opname[op]
    update = self.pop()
    dict_ = self.top()
    # print(f">>> dict: {dict_}, update: {update}")
    return DictOpInstruction(opcode.opmap[opname], block, dict=dict_,
                             update=update)
DISPATCH[opcode.opmap['DICT_MERGE']] = dict_op
DISPATCH[opcode.opmap['DICT_UPDATE']] = dict_op


class DictOpInstruction(Instruction):
    "Specialized behavior for DICT_* operations."
    def __init__(self, op, block, **kwargs):
        self.populate(("dict", "update"), kwargs)
        super().__init__(op, block, **kwargs)

    @property
    def opargs(self):
        return (self.dict, self.update)
