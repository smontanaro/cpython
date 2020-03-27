"miscellaneous"

def enumerate_reversed(seq):
    "Enumerate a sequence in reverse. Thank you Chris Angelico."
    # https://code.activestate.com/lists/python-list/706210/
    n = len(seq)
    for obj in reversed(seq):
        n -= 1
        yield (n, obj)
