"miscellaneous"

def enumerate_reversed(seq):
    "Enumerate a sequence in reverse. Thank you Chris Angelico."
    # https://code.activestate.com/lists/python-list/706210/
    n = len(seq)
    for obj in reversed(seq):
        n -= 1
        yield (n, obj)

def decode_oparg(oparg):
    "split oparg into four bytes - debug helper"
    arg4 = oparg >> 24
    arg3 = oparg >> 16 & 0xff
    arg2 = oparg >> 8 & 0xff
    arg1 = oparg & 0xff
    return (arg4, arg3, arg2, arg1)

def encode_oparg(tup):
    "smash tuple into oparg - debug helper"
    oparg = 0
    for elt in tup:
        oparg = oparg << 8 | elt
    return oparg
