[TOC]

# Rattlesnake - More Bite for Python #

Note: This is being adapted from the README file for Rattlesnake
from 2001. As such, it's not correct for the old system, nor will it
reflect the current system for awhile.

Python's current bytecode compiler generates instructions for a
stack-based virtual machine (called PyVM from here on).  While
originally fairly easy to implement, it yields a virtual machine that
runs more slowly than it might because all operands have to first be
copied to the top-of-stack.  Consider the following trivial function:

    def foo(a,b):
        return a+b

Python's bytecode compiler generates the following code:

     0 LOAD_FAST                0 (a)
     2 LOAD_FAST                1 (b)
     4 BINARY_ADD
     6 RETURN_VALUE

The first two instructions copy the values associated with the local
variables a and b to the top-of-stack so the `BINARY_ADD` opcode can
operate on them.  The result of the add operation replaces the two
values at the top-of-stack with the sum.  The `RETURN_VALUE` opcode
then returns that value to the caller.  Note that the memory locations
of a and b and the stack are only a few bytes apart, making the extra
data movement all that much more frustrating. Why not operate on them
in place?

The Rattlesnake virtual machine (RVM) changes that.  It converts PyVM
opcodes to a new three-address virtual machine.  In its initial form,
Rattlesnake generates code very similar to the existing compiler for
the above function[^shortnames][^wordcode]:

     0 EXTENDED_ARG        2
     2 LFR               512
     4 EXTENDED_ARG        3
     6 LFR               769
     8 EXTENDED_ARG        2
    10 EXTENDED_ARG      514
    12 BAR            131587
    14 RVR                 2

[^shortnames]: To keep the text from getting too wide, I've used an abbreviated
     naming scheme for the RVM opcodes. (If nothing else, it makes it
     look more like actual assembler to my old eyes.) It also helps
     distinguish between RVM instructions and PyVM instructions like
     `EXTENDED_ARG` which are still used in RVM.

[^wordcode]: Note that RVM uses the same wordcode format as PyVM, so to feed
      more than one argument to a two- or three-address instruction,
      copious use is made of the `EXTENDED_ARG` opcode. This might
      change in the future, but retaining wordcode means that the
      disassembler need not be changed immediately.

That's a bit difficult to read, so I will decode the arguments to the
load, add and return opcodes.

     0 EXTENDED_ARG       2
     2 LFR                %r2, a
     4 EXTENDED_ARG       3
     6 LFR                %r3, b
     8 EXTENDED_ARG       2
    10 EXTENDED_ARG       514
    12 BAR                %r2, %r2, %r3
    14 RVR                %r2

The `LFR` opcode works just like the current `LOAD_FAST` opcode but
copies the values to a register instead of the top-of-stack (though as
should be apparent the difference between a "register" and the "stack"
is only semantic).  The `BAR` opcode adds the contents of registers %r2
and %r3 and places the result back into %r2.  Finally, the `RVR` opcode
returns the value in %r2.

This doesn't seem any more efficient than the current VM instructions,
and in fact, it isn't.  In addition, it uses more memory than the
stack version (14 bytes vs 6) because registers must be explicitly
addressed.  However, Rattlesnake will take advantage of an interesting
property of Python frame objects, namely that the space allocated for
local variables immediately precedes the space allocated for the
frame's temporary operand stack[^frame]:

    typedef struct _frame {
        PyObject_HEAD
        ...
        PyObject **f_valuestack;   /* points after the last local */
        ...
        int f_nlocals;             /* number of locals */
        int f_stacksize;           /* size of value stack */
        PyObject *f_localsplus[1]; /* locals+stack, dynamically sized */
    } PyFrameObject;

[^frame]: The _frame declaration was extracted from the 1.5.2 frame object
     struct definition.  Python 3.9, the current base version for
     Rattlesnake, is different, but we can still make the local
     variables and stack/register adjacent.)

If we treat the local variable array and the temporary operand stack
as a contiguous array, in many instances we can operate on the values
they contain without first copying values onto the stack.  In fact, we
will consider the variables a and b to reside in registers %r0 and
%r1.  We can thus optimize out the load operations.  First, we
propagate a and b through the code where we read %r2 and %r3.  (In
what follows, I elide the `EXTENDED_ARG` opcodes, but they are really
still there where required.)

     2 LFR      %r2, a
     6 LFR      %r3, b
    12 BAR      %r2, a, b
    14 RVR      %r2

Note that we only propagate references to a until some other opcode
overwrites %r2.  Accordingly, we don't replace %r2 with a in either
the `BAR` or `RVR` opcodes.

Since %r2 and %r3 are no longer used as source operands before %r2 is
written by `BAR`, the load ops which populated them are no longer
necessary and can be deleted:

    12 BAR      %r2, a, b
    14 RVR      %r2

The end result is a reduced instruction count, less memory usage, and a
faster virtual machine.

There is strong evidence that `LOAD_FAST` is the most frequently
executed opcode in the current virtual machine[^mal].  In that message
Marc-André Lemburg showed that top-of-stack and interchange local
variables with the top of the stack (`LOAD_FAST`, `STORE_FAST` and
`POP_TOP`) accounted for about 32% of the current opcode mix.  The
existing PyVM instruction set has improved significantly in the
intervening years, but Lemburg's observations likely still correlate
strongly with reality. I believe most of those pure stack operations
could be deleted in a properly optimized three-address virtual
machine.  (Some would still be required for function call setup.)

[^mal]: http://mail.python.org/pipermail/python-dev/2000-July/007609.html

## Current Status ##

When I last worked on Rattlesnake, 1.5.2 was the current released
version of Python.  At that time, a number of instructions had not
been converted (`LOAD_NAME`, `STORE_NAME`, `DELETE_NAME`,
`SETUP_FINALLY`, `SETUP_EXCEPT`, and `IMPORT_FROM`).  In the
intervening nearly two decades(!), the PyVM instruction set has grown
significantly.

## Plans ##

A number of things must be done before the Rattlesnake optimizer is
ready for widespread testing:

* Update the converter to work with Python 3.9 (actually, targeting
  3.10/4.0).  This will include adapting dis.py to the needs of the
  Rattlesnake system as well as implementing and testing the so far
  unimplemented or untested new opcodes.

* The system should be converted to work automatically (perhaps with a
  command line flag to start).

* A number of optimizations still need to be added to the system, the
  most important being elimination of `LFR` and `SFR`.

* Finally, assuming this exercise yields the expected benefits, the
  current compiler (written in C, working from an abstract syntax
  tree) will need to be modified to generate RVM code.

## Method ##

To convert the stack-oriented opcodes into register-oriented opcodes,
you need to track the effect on the stack pointer of executing the
stack-oriented opcodes.  This is generally pretty straightforward,
though it involves some extra bookkeeping.  To properly track the
stack pointer, the code needs to first be broken up into basic blocks.
A basic block for the purposes of this discussion is a block of code
that has only a single entry point: the first instruction in the
block[^basicblock]. Consider the following simple function:

[^basicblock]: In most code optimization contexts, a basic block has only a
     single exit point as well, but we don't need the stricter
     definition here.

    def f(a):
        if a >= 5:
            return a
        return a + 5

In Python 3.8/3.9 it compiles to the following PyVM code:

          0 LOAD_FAST                   0 (a)
          2 LOAD_CONST                  1 (5)
          4 COMPARE_OP                  5 (>=)
          6 POP_JUMP_IF_FALSE          12
          8 LOAD_FAST                   0 (a)
         10 RETURN_VALUE
    >>   12 LOAD_FAST                   0 (a)
         14 LOAD_CONST                  1 (5)
         16 BINARY_ADD
         18 RETURN_VALUE

The Python disassembler module, dis, has conveniently identified
branch targets for us (those marked with ">>").  These are the first
instructions of all the basic blocks of this function.  We have two
basic blocks:

    Block 0:
          0 LOAD_FAST                   0 (a)
          2 LOAD_CONST                  1 (5)
          4 COMPARE_OP                  5 (>=)
          6 POP_JUMP_IF_FALSE          12
          8 LOAD_FAST                   0 (a)
         10 RETURN_VALUE

    Block 1:
    >>   12 LOAD_FAST                   0 (a)
         14 LOAD_CONST                  1 (5)
         16 BINARY_ADD
         18 RETURN_VALUE

Remember, the local variables and the evaluation stack are contiguous.
In this example we have a single local variable, a, so the minimum
stacklevel is 1.  When tracking the location of temporary variables we
have to know what the stacklevel is at all times so we know where to
put them later when considering the local variables and the stack as
one contiguous register file.

Let's work our way through block 0.  Remember, the stack level at the start
of the function (and thus at the start of block 0) is 1.

    Instruction          Stack Level After Execution
    -----------          ---------------------------
    LOAD_FAST              2 (pushes local var 'a')
    LOAD_CONST             3 (pushes constant 5)
    COMPARE_OP             2 (pops a & 5 and pushes the cmp result)
    POP_JUMP_IF_FALSE      1 (pops the compare result)
    LOAD_FAST              2 (pushes local var 'a')
    RETURN_VALUE           1 (pops the result it's returning)

It's important to note the stack level at the point at which the
`POP_JUMP_IF_FALSE` opcode is executed.  We know that it will jump to
another block (block 1 in this case), so we note the current stack
level and set the starting stack level of the jump's target to that.

Let's look at block 1, the target of the `POP_JUMP_IF_FALSE`
opcode. Recall that it starts with the stack level which is the
outcome of executing that instruction (1):

    Instruction          Stack Level After Execution
    -----------          ---------------------------
    LOAD_FAST              2
    LOAD_CONST             3
    BINARY_ADD             2
    RETURN_VALUE           1

Let's consider that the local variable 'a' is in register 0 (I'll use %rN to
denote register N).  That means the stack level equates to the register
number.  Let's work our way through the PyVM code one more time, generating
RVM opcodes.  To make the code a bit easier to read, I will use 'a' instead
of '%r0' and list the constant '5' instead of what would actually be an
index into the function's constants array.  Targets of JUMP opcodes are
block numbers.

RVM opcodes come with zero, one, two, three or four operands.  Two- and
three-operand instructions that write to a destination register always list
the destination register as the first operand, so to copy %r3 to %r2 it
would be written as `LOAD_FAST_REG %r2, %r3`. Also, I use block
numbers as jump targets instead of indexes into the wordcode, so
`POP_JUMP_IF_FALSE` jumps to block 1, not offset 12.

    PyVM Instructions    Stack      RVM Instructions
    -----------------    -----      ----------------
    LOAD_FAST       a      2        LFR     %r1, a
    LOAD_CONST      5      3        LCR     %r2, 5
    COMPARE_OP      >=     2        COR     %r1, %r1, %r2, >=
    POP_JUMP_IF_FALSE   1  1        JIFR    %r1, 1
    LOAD_FAST       a      2        LFR     %r1, a
    RETURN_VALUE           1        RVR     %r1

    LOAD_FAST       a      2        LFR     %r1, a
    LOAD_CONST      5      3        LCR     %r2, 5
    BINARY_ADD             2        BAR     %r1, %r1, %r2
    RETURN_VALUE           1        RVR     %r1

The sequence of steps when converting a `LOAD_FAST` opcode is:

1. The destination register (DST) is the return value of push().
2. Generate `LFR %rDST, x`, where x is the local variable.

Generating code for other opcodes is similar.  To generate a
`BAR` instruction, the sequence of steps is:

1. The right-hand operand (SRC2) is the return value of pop().
2. The left-hand operand (SRC1) is the return value of pop().
3. The result (destination, DST) is the return value of push().
4. Generate `BAR %rDST, %rSRC1, %rSRC2`.

Let's now try optimizing the RVM code.  In the original Rattlesnake,
any functions which returned explicit values could well never fall off
the end of the last block, so the obligatory `LOAD_CONST
None/RETURN_VALUE` pair which the compiler always generated was often
dead code. Refinements to PyVM have improved many aspects of code
generation, including dead code elimination. As the RVM code is
generated and optimized, dead code elimination may well be necessary
again.

[]: # (Commented lines follow...)

[]: # (I'll take the position that the less code I have to look at, the)
[]: # (better, so even though deleting dead code doesn't speed anything up,)
[]: # (it makes it easier to see the rest of the code.  The JUMP_FORWARD_REG)
[]: # (opcode and the LOAD_CONST_REG/RETURN_VALUE_REG are all dead code)
[]: # (because they occur immediately after an unconditional branch in the)
[]: # (same block of code as the branch.  That "in the same block" condition)
[]: # (prevents us from considering the POP_TOP_REG (first instruction in)
[]: # (block 1) after the JUMP_FORWARD_REG (last instruction in block 2) as)
[]: # (dead code.)
[]: # ()
[]: # (So, here's the RVM code after dead code elimination.  Note that after the)
[]: # (JUMP_FORWARD_REG opcode is deleted we are left with just two basic blocks:)
[]: # ()
[]: # (    LOAD_FAST_REG       %r1, a)
[]: # (    LOAD_CONST_REG      %r2, 5)
[]: # (    COMPARE_OP_REG      %r1, %r1, %r2, >=)
[]: # (    JUMP_IF_FALSE_REG   1)
[]: # (    POP_TOP_REG)
[]: # (    LOAD_FAST_REG       %r1, a)
[]: # (    RETURN_VALUE_REG    %r1)
[]: # ()
[]: # (    POP_TOP_REG)
[]: # (    LOAD_FAST_REG       %r1, a)
[]: # (    LOAD_CONST_REG      %r2, 5)
[]: # (    BINARY_ADD_REG      %r1, %r1, %r2)
[]: # (    RETURN_VALUE_REG    %r1)

Now let's turn our attention to those `LFR` opcodes.  If local
variable 'a' is actually in %r0 already, we don't need to copy it to
%r1 before using it.  So, anywhere we read %r1, replace it with 'a'
(until another opcode overwrites %r1).  Block 0 thus becomes

    LFR        %r1, a
    LCR        %r2, 5
    COR        %r1, a, %r2, >=
    JIFR       %r1, 1
    LFR        %r1, a
    RVR        a

One reason for not using the %rN notation for local variables is to
maintain the distinction between user-defined state (local variables)
and intermediate scratch state (stack/register) values.  Any time we
load a value into a register, but then overwrite it or return from the
function before referencing it, we can delete the instruction that
modified the register.  Scanning from the start of the block, we see
that %r1 is modified in the first instruction, but that `COR`
overwrites it two steps later, so we can toss the LOAD.  Similarly,
the second `LFR` result is not used before the function returns, so it
can be deleted as well.  This leaves us with

    LCR    %r2, 5
    COR    %r1, a, %r2, >=
    JIFR   %r1, 1
    RVR    a

Let's apply the same two rules (access local variables directly and discard
unused loads) to block 1:

    LCR     %r2, 5
    BAR     %r1, a, %r2
    RVR     %r1

When all is said and done, we are left with

    LCR    %r2, 5
    COR    %r1, a, %r2, >=
    JIFR   %r1, 1
    RVR    a

    LCR     %r2, 5
    BAR     %r1, a, %r2
    RVR     %r1

Which should be faster than the original PyVM code. It might not be
smaller.  Don't forget there are also a number of `EXTENDED_ARG`
opcodes which we've elided for simplicity. Any time an opcode requires
more than one argument, they will be needed.

## Possible Optimizations ##

### Eliminate Constant Loads ###

We could go even further.  Suppose that at frame creation time we
copied the code object's constants into the frame. Layout of the
`f_localsplus` segment might thus be something like:

    constants
    local variables
    stack/registers
    cells & free variables

We could thus eliminate `LCR` opcodes as well. All Python functions
have at least one constant, None.  In this case we also have the
integer constant, 5.  Adding them to the local registers would extend
the local variables by two elements, thus making the starting stack
level 3 instead of 1.  (None in %r0, 5 in %r1, and a in %r2).  I won't
go through all the steps again, but note that the RVM code would
convert to

    COR      %r3, a, 5, >=
    JIFR     %r3, 1
    RVR      a

    BAR      %r3, a, 5
    RVR      %r3

Even shorter and faster!

### Track Globals ###

Global variables and attributes rarely change.  For example, once a function
imports the math module, the binding between the name "math" and the module
it refers to aren't likely to change.  Similarly, if the function that uses
the math module refers to its "sin" attribute, it's unlikely to change.
Still, every time the module wants to call the math.sin function, it must
first execute a pair of instructions:

    LOAD_GLOBAL        math
    LOAD_ATTR          sin

What if the client module always assumed that math.sin was a local constant
and it was the responsibility of "external forces" outside the function to
keep the reference correct?  We might have code like this:

    TRACK              math.sin
    ...
    LOAD_FAST          math.sin
    ...
    UNTRACK            math.sin

If the LOAD_FAST was in a loop the payoff in reduced global loads and
attribute lookups could be significant.

This technique could, in theory, be applied to any global variable access or
attribute lookup.  Consider this code:

    l = []
    for i in range(10):
        l.append(math.sin(i))
    return l

Even though l is a local variable, you still pay the cost of loading
l.append ten times in the loop.  The compiler (or an optimizer) could
recognize that both math.sin and l.append are being called in a loop and
decide to generate the tracked global code, avoiding it for the builtin
range() function since it's only called once before the loop.  The RVM
bytecode generated might look like so (don't pay real close attention to the
register assignments):

[]: # (* Totally not ready for prime time *)
[]: # ()
[]: # (    BLR         l, 0)
[]: # (    TRACK       %r2, math.sin)
[]: # (    TRACK       %r3, l.append)
[]: # (    LGR         %r4, range)
[]: # (    LCR         %r5, 10)
[]: # (    CFR         %r4, %r5, 1)
[]: # (    GET_ITER)
[]: # ()
[]: # (    FOR_ITER    20 (to 34))
[]: # (             14 STORE_FAST               1 (i))
[]: # ()
[]: # (            16 LOAD_FAST                0 (l))
[]: # (             18 LOAD_METHOD              1 (append))
[]: # (             20 LOAD_GLOBAL              2 (math))
[]: # (             22 LOAD_METHOD              3 (sin))
[]: # (             24 LOAD_FAST                1 (i))
[]: # (             26 CALL_METHOD              1)
[]: # (             28 CALL_METHOD              1)
[]: # (             30 POP_TOP)
[]: # (             32 JUMP_ABSOLUTE           12)
[]: # ()
[]: # (       >>   34 LOAD_FAST                0 (l))
[]: # (             36 RETURN_VALUE)
[]: # ()
[]: # (    BLR    l, 0)
[]: # (    TRACK      %r2, math.sin)
[]: # (    TRACK      %r3, l.append)
[]: # (    SETUP_LOOP_REG    i)
[]: # (    LOAD_GLOBAL_REG   %r4, range)
[]: # (    LOAD_CONST_REG    %r5, 10)
[]: # (    CALL_FUNCTION     1, 0, %r4)
[]: # (    LOAD_CONST_REG    i, 0)
[]: # (    FOR_LOOP          i)
[]: # (    LOAD_FAST_REG     %r5, l.append)
[]: # (    LOAD_FAST_REG     %r6, math.sin)
[]: # (    LOAD_FAST_REG     %r7, i)
[]: # (    CALL_FUNCTION     1, 0, %r6)
[]: # (    CALL_FUNCTION     1, 0, %r5)
[]: # (    POP_TOP)
[]: # (    JUMP_ABSOLUTE)
[]: # (    POP_BLOCK)
[]: # (    UNTRACK    %r3, l.append)
[]: # (    UNTRACK    %r2, math.sin)
[]: # (    RETURN_VALUE_REG  l)

[]: # (The effect of the TRACK opcode would be to perform any necessary)
[]: # (object and attribute loads and notify the respective objects that those)
[]: # (values should be tracked.  The register argument tells the object what)
[]: # (location needs to be updated.  If, for some reason, the binding of the name)
[]: # ("math" changes, the function's module would perform the rebinding, look up)
[]: # (the new object's "sin" attribute, copy it into place, and notify the new)
[]: # (object to track its "sin" attribute.  The UNTRACK instructions would)
[]: # ("unregister" the object tracking.)
[]: # ()
[]: # (This should be thread-safe, thanks to the global interpreter lock and the)
[]: # (granularity of thread switching.  There would never be very many objects)
[]: # (tracked at any one time, just those in use the currently active frames in)
[]: # (each running thread.)
[]: # ()
[]: # (Let's look at a somewhat higher level at the main function of pystones.py:)
[]: # ()
[]: # (    def Proc0(loops=LOOPS):)
[]: # (    global IntGlob)
[]: # (    global BoolGlob)
[]: # (    global Char1Glob)
[]: # (    global Char2Glob)
[]: # (    global Array1Glob)
[]: # (    global Array2Glob)
[]: # (    global PtrGlb)
[]: # (    global PtrGlbNext)
[]: # ()
[]: # (    starttime = clock())
[]: # (    for i in range(loops):)
[]: # (        pass)
[]: # (    nulltime = clock() - starttime)
[]: # ()
[]: # (    PtrGlbNext = Record())
[]: # (    PtrGlb = Record())
[]: # (    PtrGlb.PtrComp = PtrGlbNext)
[]: # (    PtrGlb.Discr = Ident1)
[]: # (    PtrGlb.EnumComp = Ident3)
[]: # (    PtrGlb.IntComp = 40)
[]: # (    PtrGlb.StringComp = "DHRYSTONE PROGRAM, SOME STRING")
[]: # (    String1Loc = "DHRYSTONE PROGRAM, 1'ST STRING")
[]: # (    Array2Glob[8][7] = 10)
[]: # ()
[]: # (    starttime = clock())
[]: # ()
[]: # (    for i in range(loops):)
[]: # (        Proc5())
[]: # (        Proc4())
[]: # (        IntLoc1 = 2)
[]: # (        IntLoc2 = 3)
[]: # (        String2Loc = "DHRYSTONE PROGRAM, 2'ND STRING")
[]: # (        EnumLoc = Ident2)
[]: # (        BoolGlob = not Func2(String1Loc, String2Loc))
[]: # (        while IntLoc1 < IntLoc2:)
[]: # (        IntLoc3 = 5 * IntLoc1 - IntLoc2)
[]: # (        IntLoc3 = Proc7(IntLoc1, IntLoc2))
[]: # (        IntLoc1 = IntLoc1 + 1)
[]: # (        Proc8(Array1Glob, Array2Glob, IntLoc1, IntLoc3))
[]: # (        PtrGlb = Proc1(PtrGlb))
[]: # (        CharIndex = 'A')
[]: # (        while CharIndex <= Char2Glob:)
[]: # (        if EnumLoc == Func1(CharIndex, 'C'):)
[]: # (            EnumLoc = Proc6(Ident1))
[]: # (        CharIndex = chr(ord(CharIndex)+1))
[]: # (        IntLoc3 = IntLoc2 * IntLoc1)
[]: # (        IntLoc2 = IntLoc3 / IntLoc1)
[]: # (        IntLoc2 = 7 * (IntLoc3 - IntLoc2) - IntLoc1)
[]: # (        IntLoc1 = Proc2(IntLoc1))
[]: # ()
[]: # (    benchtime = clock() - starttime - nulltime)
[]: # (    return benchtime, (loops / benchtime))
[]: # ()
[]: # (If we look at the loop, we see the following global symbol references:)
[]: # (Char2Glob, Array1Glob, Array2Glob, Proc1, Proc2, Proc4, Proc5, Proc6, Proc7,)
[]: # (Proc8, Ident1, Ident2, Func2, chr, and ord.  That's a minimum of 15)
[]: # (LOAD_GLOBAL instructions that could be either converted to LOAD_FAST)
[]: # (instructions (in PyVM) or eliminated altogether (in RVM) each pass through)
[]: # (the outer loop.  Proc7 is called each pass in the first inner while loop and)
[]: # (Char2Glob, Func1, Proc6, chr and ord are called each pass in the second)
[]: # (inner while loop, so the payoff for those objects would be even greater.)
