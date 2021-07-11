"miscellaneous"

import dis as _dis
import opcode

EXT_ARG_OPCODE = opcode.opmap["EXTENDED_ARG"]
NOP_OPCODE = opcode.opmap['NOP']

CO_REGISTER = None
for _val in _dis.COMPILER_FLAG_NAMES:
    if _dis.COMPILER_FLAG_NAMES[_val] == "REGISTER":
        CO_REGISTER = _val
        break
assert CO_REGISTER is not None
del _val

def enumerate_reversed(seq):
    "Enumerate a sequence in reverse. Thank you Chris Angelico."
    # https://code.activestate.com/lists/python-list/706210/
    num = len(seq)
    for obj in reversed(seq):
        num -= 1
        yield (num, obj)

def decode_oparg(oparg, minimize=True):
    """Split oparg into (up to) four bytes.

    If minimize is True (default), leading zeros will be trimmed from
    the tuple.

    """
    if not oparg:
        return (0,)
    args = [
        oparg >> 24,
        oparg >> 16 & 0xff,
        oparg >> 8 & 0xff,
        oparg & 0xff,
    ]
    if minimize:
        while args and args[0] == 0:
            del args[0]
    return tuple(args)

def encode_oparg(tup):
    "smash tuple back into oparg int"
    oparg = 0
    for elt in tup:
        oparg = oparg << 8 | elt
    return oparg

# pylint: disable=too-few-public-methods
class LineNumberDict:
    """Return line number associated with max key <= user's key.

    For example, if we have:

    fdict = LineNumberDict(func.__code__)

    where func.__code__'s lnotab looks like this dict:

    {0: 4, 6: 5, 16: 6, 26: 7}

    fdict[16] returns 6, but fdict[15] returns 5. Any key greater than
    26 would return 7.  Any key less than the smallest key would raise
    KeyError.  If a max key value is set, e.g.:

    fdict = LineNumberDict(func.__code__, maxkey=36)

    any key greater than that would also raise KeyError.

    """

    def __init__(self, codeobj=None, maxkey=None):
        self.src_dict = {}
        for (byt, lno) in _dis.findlinestarts(codeobj):
            self.src_dict[byt] = lno
        self.maxkey = maxkey
        self.minkey = min(self.src_dict)
        self.true_maxkey = max(self.src_dict)

    def __getitem__(self, key):
        if (key < self.minkey or
            self.maxkey is not None and key > self.maxkey):
            raise KeyError(f"Key {key} out of range.")

        if key > self.true_maxkey:
            return self.src_dict[self.true_maxkey]

        while True:
            val = self.src_dict.get(key, None)
            if val is not None:
                return val
            key -= 1

    def __repr__(self):
        return f"<LineNumberDict: {self.src_dict}>"
    __str__ = __repr__

class StackSizeException(Exception):
    """Raised when the stack would grow too small or too large.

    See bpo40315.
    """
