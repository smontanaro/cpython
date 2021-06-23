"""NOTE: This comes from the old Rattlesnake work. It's useful here
initially as documentation of how I did things way back when. The more
I struggle with the current AST-based compiler, the more I think I
will revert to this method as proof-of-concept. Let someone else make
it production-ready if it proves to be worthwhile.

In the new formulation, I plan to retain 16-bit word code, relying
on EXTENDED_ARGS to encode extra arguments where necessary.

No matter how many arguments there are, the overall instruction is
encoded as follows (my math needs to be checked here):

* Big endian: (OP << 8 | ARG1) << 16 | (ARG2 << 8 | ARG3)

* Little endian: (OP | ARG1 << 8) << 16 | (ARG2 | ARG3 << 8)

The two-arg and three-arg cases require, respectively, one or two
EXTENDED_ARG opcodes ahead of them. EXTENDED_ARG works by saving the
current oparg, setting the next opcode and oparg, shifting the old
oparg by 8 bits, then oring that with the new oparg. It then jumps
directly to the next opcode. I doubt the performance hit would be
much, since EXTENDED_ARG is so minimal, a couple bitwise operations
and a jump.

Using EXTENDED_ARG should solve the problem of trying to squeeze four
args into 32 bits for COMPARE_OP. oparg can be up to four bytes. That
really requires four arguments, the comparison operator as well as
destination and two source registers. In the quad-byte opcode
formulation I could only easily squeeze three operand arg bytes into
the instruction. With word code I can just punt and offer up three
EXTENDED_ARG instructions before COMPARE_OP.

EXTENDED_ARG dst
EXTENDED_ARG src1
EXTENDED_ARG src2
COMPARE_OP operator

The oparg constructed by the three EXTENDED_ARG opcodes and COMPARE_OP
itself would be

(((dst << 8) | src1) << 8 | src2) << 8 | operator & 0xff

or

dst << 24 | src1 << 16 | src2 << 8 | operator

It would be nice if oparg was unsigned, but I doubt it will be a
practical problem that it's not. I think you can just say that the
number of locals and stack or registers is limited to 127 in the
CPython implementation. (This suggests a simple check during
execution, asserting that co_nlocals + co_stacksize <= 127.)

"""

import dis
import sys

from rvm.converter import InstructionSetConverter

__version__ = "0.0"


_A_GLOBAL = 42
def h(s, b):
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
        s = b + 4
        b = s - 21
        return s
    return b - 1

def main():
    for func in (h,):
        print("---", func, "---")
        isc = InstructionSetConverter(func.__code__)
        isc.gen_rvm()
        print("Blocks right after gen_rvm()")
        isc.display_blocks(isc.blocks["RVM"])
        isc.forward_propagate_fast_loads()
        print("Blocks right after forward propagation")
        isc.display_blocks(isc.blocks["RVM"])
        isc.delete_nops()
        print("Blocks right after NOP removal")
        isc.display_blocks(isc.blocks["RVM"])
        func.__code__ = func.__code__.replace(co_code=bytes(isc))
        dis.dis(func)

    return 0

if __name__ == "__main__":
    try:
        result = main()
    except (KeyboardInterrupt, BrokenPipeError):
        result = 0
    sys.exit(result)
