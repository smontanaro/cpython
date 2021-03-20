#!/usr/bin/env python

"""Simple script to help adjust to changes to opcode ordering.

This happens when new instructions are added to PyVM. When I adjust to
them, the ordering necessarily changes.  I've only seen problems in
test_dis.py.

Example usage: python mapopcodes.py < Lib/test/test_dis.py > Lib/test/test_dis.py.new

"""


from opcode import opmap
import re
import sys

for (i, line) in enumerate(sys.stdin):
    if re.match(r" +Instruction\(", line) is not None:
        mat = re.search("opname='([A-Z_]+)', opcode=([0-9]+)", line)
        if mat is None:
            print("Couldn't match:", repr(line), file=sys.stderr)
            continue
        name = mat.group(1)
        opcode = int(mat.group(2))
        if opmap[name] != opcode:
            line = re.sub("opcode=[0-9]+", f"opcode={opmap[name]}", line)
            print("line", i, name, opcode, "->", opmap[name], file=sys.stderr)
    print(line, end="")
