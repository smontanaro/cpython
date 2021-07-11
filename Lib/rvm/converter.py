"The actual converter class"

import opcode

from .blocks import Block
from .instructions import PyVMInstruction, NOPInstruction
from .util import (enumerate_reversed, LineNumberDict,
                              StackSizeException)
from .jump import JumpInstruction
from .function import CallInstruction
from .loadstore import LoadFastInstruction, StoreFastInstruction
from .sequence import BuildSeqInstruction

from .util import NOP_OPCODE, EXT_ARG_OPCODE

class InstructionSetConverter:
    """Convert stack-based VM code into register-oriented VM code.

    This class consists of a series of small methods, each of which
    knows how to convert a small number of stack-based instructions to
    their register-based equivalents.  A dispatch table keyed by the
    stack-based opcodes selects the appropriate routine.

    """

    def __init__(self, codeobj):
        """input must be a code object."""
        self.codeobj = codeobj
        self.codestr = codeobj.co_code
        self.locals = codeobj.co_varnames
        self.globals = codeobj.co_names
        self.constants = codeobj.co_consts
        self.nlocals = codeobj.co_nlocals
        self.stacksize = codeobj.co_stacksize
        self.blocks = {
            "PyVM": [],
            "RVM": [],
        }

        # Stack starts right after locals. Together, the locals and
        # the space allocated for the stack form a single register
        # file.
        self.stacklevel = self.nlocals
        self.max_stacklevel = self.nlocals + self.stacksize

        # print(">> nlocals:", self.nlocals)
        # print(">> stacksize:", self.stacksize)
        # print(">> starting stacklevel:", self.stacklevel)
        # print(">> max stacklevel:", self.max_stacklevel)
        assert self.max_stacklevel <= 127, "locals+stack are too big!"

    def findlabels(self, code):
        "Find target addresses in the code."
        labels = {0}
        n = len(code)
        carry_oparg = 0
        for i in range(0, n, 2):
            op, oparg = code[i:i+2]
            carry_oparg = carry_oparg << 8 | oparg
            if op == EXT_ARG_OPCODE:
                continue
            oparg, carry_oparg = carry_oparg, 0
            if op in opcode.hasjrel:
                # relative jump
                labels.add(i + 2 + oparg)
                #print(i, "labels:", labels)
            elif op in opcode.hasjabs:
                # abs jump
                labels.add(oparg)
                #print(i, "labels:", labels)
        labels = sorted(labels)
        return labels

    def convert_jump_targets_to_blocks(self):
        "Convert jump target addresses to block numbers in PyVM blocks."
        blocks = self.blocks["PyVM"]
        for block in blocks:
            for instr in block:
                if instr.is_jump():
                    for tblock in blocks:
                        if instr.target_address == tblock.address:
                            instr.target = tblock.block_number
                            break
                    assert instr.target != -1
                    # No longer required.
                    del instr.target_address

    def find_blocks(self):
        """Convert code byte string to block form.

        JUMP instruction targets are converted to block numbers at the end.

        """
        blocks = self.blocks["PyVM"]
        labels = self.findlabels(self.codestr)
        line_numbers = LineNumberDict(self.codeobj)
        #print("line numbers:", line_numbers)
        #print(">>> labels:", labels)
        n = len(self.codestr)
        block_num = 0
        ext_oparg = 0
        for offset in range(0, n, 2):
            if offset in labels:
                block = Block("PyVM", self, block_num)
                block.address = offset
                #print(">>> new block:", block, "@", offset)
                block_num += 1
                blocks.append(block)
            (op, oparg) = self.codestr[offset:offset+2]
            #print(">>>", op, opcode.opname[op], oparg)
            # Elide EXTENDED_ARG opcodes, constructing the effective
            # oparg as we go.
            if op == EXT_ARG_OPCODE:
                ext_oparg = ext_oparg << 8 | oparg
            else:
                oparg = ext_oparg << 8 | oparg
                instr = PyVMInstruction(op, block, opargs=(oparg,))
                if instr.is_jump():
                    address = oparg
                    if instr.is_rel_jump():
                        # Convert to absolute
                        address += offset + 2
                    #print(f">> {block.block_number} found a JUMP"
                    #      f" @ {offset} target_addr={address}")
                    instr = JumpInstruction(op, block, target_address=address)
                instr.line_number = line_numbers[offset]
                #print(">>>", instr)
                block.append(instr)
                ext_oparg = 0
        self.convert_jump_targets_to_blocks()

    def set_block_stacklevel(self, target, level):
        """set the input stack level for particular block"""
        #print(">> set_block_stacklevel:", (target, level))
        self.blocks["RVM"][target].set_stacklevel(level)

    # series of operations below mimic the stack changes of various
    # stack operations so we know what slot to find particular values in
    def push(self):
        """increment and return next writable slot on the stack"""
        self.stacklevel += 1
        #print(">> push:", self.stacklevel)
        # This gets a bit tricky.  In response to an issue I opened,
        # bpo40315, Serhiy Storchaka wrote:

        # > [U]nreachable code is left because some code (in
        # > particularly the lineno setter of the frame object)
        # > depends on instructions which may be in the unreachable
        # > code to determine the boundaries of programming blocks. It
        # > is safer to keep some unreachable code.

        # > You can just ignore the code which uses the stack past
        # > co_stacksize.

        # So, I think we can raise a special exception (AssertionError
        # seems a bit general) here, and in those convert functions
        # where the stack only grows (mostly LOADs, but eventually
        # IMPORTs as well), we can catch and ignore it.
        if self.stacklevel > self.max_stacklevel:
            raise StackSizeException(
                f"Overran the allocated stack/register space!"
                f" {self.stacklevel} > {self.max_stacklevel}"
            )
        return self.stacklevel - 1

    def pop(self):
        """return top readable slot on the stack and decrement"""
        self.stacklevel -= 1
        #print(">> pop:", self.stacklevel)
        if self.stacklevel < self.nlocals:
            raise StackSizeException(
                f"Stack slammed into locals!"
                f" {self.stacklevel} < {self.nlocals}"
            )
        return self.stacklevel

    def peek(self, n):
        """return n'th readable slot in the stack without decrement."""
        if self.stacklevel - n < self.nlocals:
            raise StackSizeException(
                f"Peek read past bottom of locals!"
                f" {self.stacklevel - n} < {self.nlocals}"
            )
        return self.stacklevel - n

    def top(self):
        """return top readable slot on the stack"""
        #print(">> top:", self.stacklevel)
        return self.stacklevel - 1

    def gen_rvm(self):
        "Generate a series of blocks containing RVM instructions."
        self.find_blocks()
        self.blocks["RVM"] = []
        for pyvm_block in self.blocks["PyVM"]:
            rvm_block = Block("RVM", self, block_number=pyvm_block.block_number)
            self.blocks["RVM"].append(rvm_block)
        for (rvm, pyvm) in zip(self.blocks["RVM"], self.blocks["PyVM"]):
            pyvm.gen_rvm(rvm)

    # A small, detailed example forward propagating the result of a
    # fast load and backward propagating the result of a fast
    # store. (Using abbreviated names: LFR == LOAD_FAST_REG, etc.)

    #                       Forward    Reverse     Action
    # LFR, (2, 1)           %r2 -> %r1             NOP
    # LCR, (3, 1)               |
    # BMR, (2, 3, 2)            v          ^       src2 = %r1, dst = %r0
    # SFR, (0, 2)                      %r2 -> %r0  NOP

    # Apply actions:

    # NOP
    # LCR, (3, 1)
    # BMR, (0, 3, 1)
    # NOP

    # Delete NOPs:

    # LCR, (3, 1)
    # BMR, (0, 3, 1)

    # Result:

    # * 10 bytes in code string instead of 18

    # * Two operations, three EXT_ARG instead of four operations, five
    #   EXT_ARG

    # * One load instead of two

    # * No explicit stores

    # Consider forward propagation operating on a few
    # instructions. Before:

    #  0 Instruction(LOAD_FAST_REG, (2, 0)) (4)
    #  4 Instruction(LOAD_FAST_REG, (3, 1)) (4)
    #  8 Instruction(COMPARE_OP_REG, (2, 2, 3, 4)) (8)
    # 16 Instruction(JUMP_IF_FALSE_REG, (1, 2)) (4)
    # 20 Instruction(LOAD_FAST_REG, (2, 1)) (4)
    # 24 Instruction(LOAD_CONST_REG, (3, 1)) (4)
    # 28 Instruction(BINARY_SUBTRACT_REG, (2, 2, 3)) (6)

    # Immediately after:

    #  0 Instruction(NOP, (0,)) (2)
    #  2 Instruction(NOP, (0,)) (2)
    #  4 Instruction(COMPARE_OP_REG, (2, 0, 1, 4)) (8)
    # 12 Instruction(JUMP_IF_FALSE_REG, (1, 2)) (4)
    # 16 Instruction(NOP, (0,)) (2)
    # 18 Instruction(LOAD_CONST_REG, (3, 1)) (4)
    # 22 Instruction(BINARY_SUBTRACT_REG, (2, 1, 1)) (6)

    # When the first two LFR instructions were added to the block, we
    # push()'d, indicating that registers 2 and 3 were occupied.  When
    # forward propagation replaces them with NOPs, I think we need to
    # at least note that they are now free. pop() might not be the
    # right thing to do, as we have already added a LCR instruction
    # whose destination was register 3.  Maybe we maintain a register
    # free list?  Or maybe it doesn't matter.  We just don't use as
    # many registers.  Perhaps when someone implements a better
    # register allocation scheme the registers which were freed up in
    # this stage will be useful.

    # Note: At one point I had a backward_propagate_fast_stores method
    # as well, but analysis of a failing test showed that both forward
    # and backward propagation (at least as I'd implemented them)
    # caused problems, so I removed backward_propagate_fast_stores.

    def forward_propagate_fast_loads(self):
        """Remove most LOAD_FAST_REG instructions.

        Propagate forward source register where destination register
        is used.

        """
        self.mark_protected_loads()
        prop_dict = {}
        dirty = None
        for block in self.blocks["RVM"]:
            nop = NOPInstruction(NOP_OPCODE, block)
            for (i, instr) in enumerate(block):
                # Check for possible mappings in this instruction,
                # even if it is a load/store which might be replaced
                # below.
                for srckey in ("source1", "source2"):
                    src = getattr(instr, srckey, None)
                    if src is not None:
                        newval = prop_dict.get(src, src)
                        if newval != src:
                            #print("Set up mapping from", src, "to", newval)
                            pass
                        setattr(instr, srckey, newval)
                dst = getattr(instr, "dest", None)
                if dst is not None:
                    # If the destination register is overwritten,
                    # remove it from the dictionary as it's no
                    # longer valid.
                    try:
                        del prop_dict[dst]
                    except KeyError:
                        pass
                if (isinstance(instr, LoadFastInstruction) and
                    not instr.protected):
                    # Will map future references to the load's
                    # destination register to its source.
                    #print("will map", instr.dest, "to", instr.source1)
                    prop_dict[instr.dest] = instr.source1
                    # The load is no longer needed, so replace it with
                    # a NOP.
                    #print("replace", block[i], "with", nop)
                    block[i] = nop
                    if dirty is None:
                        dirty = block.block_number
        self.mark_dirty(dirty)

    def mark_protected_loads(self):
        "Identify fast loads and stores which must not be removed."
        # Sometimes registers are used implicitly, so LOADs into them
        # can't be removed so easily.  Consider the code necessary to
        # construct this list:
        #
        # [1, x, y]
        #
        # Basic RVM code looks like this (ignoring EXT_ARG instructions):
        #
        # LOAD_CONST_REG       769 (%r3 <- 1)
        # LOAD_FAST_REG       1024 (%r4 <- %r0)
        # LOAD_FAST_REG       1281 (%r5 <- %r1)
        # BUILD_LIST_REG    131843 (0, 2, 3, 3)
        #
        # The BUILD_LIST_REG instruction requires that its inputs be in
        # registers %r3 through %r5.  Accordingly, the two LOAD_FAST_REG
        # instructions used to (partially) construct its inputs must be
        # preserved.  BUILD_TUPLE_REG and CALL_FUNCTION_REG will have
        # similar implicit references.  Other instructions might as well.
        # One way to deal with this might be to identify such implicit
        # uses and mark the corresponding LOADs as "protected."  Then
        # execute the normal forward propagation code, skipping over those
        # LOADs.
        #
        # This example is more challenging:
        #
        # def _tuple(a):
        #     return (a, a+2, a+3, a+4)
        #
        # Note that the LOAD_FAST_REG of the initial 'a' won't
        # immediately precede the BUILD_TUPLE_REG instruction. The
        # various expression evaluations separate them.  Instead of
        # just looking at the immediately preceding instr.length
        # instructions and marking LOAD_FAST_REG as protected, we need
        # to look at the last writes to all registers between
        # instr.dest and instr.dest+instr.length
        #
        # I've hacked something together here.  Not sure it's entirely
        # correct. It's certainly still incomplete, failing to
        # consider calls at this point), but the failing test passes,
        # so we're done. :-)
        for block in self.blocks["RVM"]:
            for (i, instr) in enumerate(block):
                if isinstance(instr, BuildSeqInstruction):
                    first = instr.dest
                    last = first + instr.length
                elif isinstance(instr, CallInstruction):
                    first = instr.dest
                    last = first + instr.nargs
                else:
                    # Maybe others not yet handled?
                    continue
                saved = {}
                reg = first
                while reg < last:
                    saved[reg] = False
                    reg += 1

                # Look backward to find writes to the registers in
                # the saved dict.
                for index in range(i - 1, -1, -1):
                    reg = getattr(block[index], "dest", None)
                    if reg not in saved:
                        # No mention of any of our registers.
                        continue
                    if saved[reg]:
                        # This operation is earlier than the
                        # latest write to reg, so it's okay to
                        # elide it.
                        continue
                    if hasattr(block[index], "protected"):
                        # One of our registers is mentioned in a
                        # LOAD, so protect it and mark the
                        # register as saved.
                        block[index].protected = True
                        saved[reg] = True
                    if all(saved.values()):
                        # We've protected every LOAD into one of
                        # our registers, so we're done
                        break
                else:
                    # We got here without marking every register
                    # of interest saved.  That's okay, as not
                    # everything which affects our input registers
                    # will be a LOAD.
                    pass

    def delete_nops(self):
        "NOP instructions can safely be removed."
        dirty = None
        for block in self.blocks["RVM"]:
            for (i, instr) in enumerate_reversed(block):
                if isinstance(instr, NOPInstruction):
                    del block[i]
                    if dirty is None:
                        dirty = block.block_number
                    else:
                        dirty = min(block.block_number, dirty)
        self.mark_dirty(dirty)

    def mark_dirty(self, dirty):
        "Reset addresses on dirty blocks."
        # Every block downstream from the first modified block is
        # dirty.
        if dirty is None:
            return
        for block in self.blocks["RVM"][dirty:]:
            #print("??? mark block", block.block_number, "dirty")
            block.address = -1
        # Except the address of the first block is always known.
        # pylint: disable=protected-access
        self.blocks["RVM"][0]._address = 0

    def display_blocks(self, blocks):
        "debug"
        print("globals:", self.globals)
        print("locals:", self.locals)
        print("constants:", self.constants)
        print("code len:", sum(block.codelen() for block in blocks))
        print("first lineno:", self.codeobj.co_firstlineno)
        print("stack size:", self.stacksize)
        for block in blocks:
            print(block)
            block.display()
        print()


    def __bytes__(self):
        "Return generated byte string."
        instr_bytes = []
        for block in self.blocks["RVM"]:
            instr_bytes.append(bytes(block))
        return b"".join(instr_bytes)

    # Described in Objects/lnotab_notes.txt and Objects/codeobject.c:emit_delta.
    def get_lnotab(self):
        #print("\nget_lnotab", self)
        firstlineno = self.codeobj.co_firstlineno
        start = end = 0
        lnotab = []
        for block in self.blocks["RVM"]:
            for instr in block.instructions:
                #print(instr)
                line_number = instr.line_number - firstlineno
                end = start + len(instr)
                lnotab.append((start, end, line_number))
                start = end
        last_line = 0
        tab = []
        last_byte = 0
        for (start, end, line) in lnotab:
            #print("lnotab:", (start, end, line))
            delta = end - last_byte
            last_byte = end
            offset = line - last_line
            while delta > 255:
                tab.extend((255, 0))
                #print("tab:", tab[-2:])
                delta -= 255
            while offset > 127:
                tab.extend((delta, 127))
                #print("tab:", tab[-2:])
                delta = 0
                offset -= 127
            if offset < 0:
                tab.extend((delta, 255))
            else:
                tab.extend((delta, offset))
            #print("tab:", tab[-2:])
            last_line = line
        tab.append(255)
        #print("tab:", tab)
        #print("lnotab:", lnotab)
        return bytes(tab)
