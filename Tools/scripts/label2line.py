#!/usr/bin/env python

"""Map break-by-label to break-by-line-number in gdb file.

Note: This appears to perhaps only be necessary in (some)
Ubuntu-derived Linux installations:

https://sourceware.org/bugzilla/show_bug.cgi?id=27907

GDB allows you to set breakpoints at labels.  That seems not to be
working for me, breaking at odd/incorrect locations.  Until I figure
that out (or GCC/GDB get fixed), this little script can be used to map
break commands like:

break ceval_reg.h:_PyEval_EvalFrameDefault:TARGET_CONTAINS_OP_REG

to break commands like this:

break ceval_reg.h:408

Usage: label2line < something.gdb > something-else.gdb

You would then source something-else.gdb in your GDB sessions.

Note that in Python's virtual machine, a label like
TARGET_CONTAINS_OP_REG actually appears in the code as
TARGET(CONTAINS_OP_REG), so that special case needs to be handled.
Also, GDB usage only specifies the filename, not the path leading up
to it, so the program needs to find the true location of the source
file as well...

"""

import glob
import os
import re
import sys

def main():
    file_map = find_source_files()
    process_gdb_file(file_map, sys.stdin, sys.stdout)
    return 0

def process_gdb_file(file_map, fin, fout):
    """Read lines from fin, mapping breaks at labels to breaks at lines."""
    brk = re.compile(r"\s*br(?:eak)?\s+(?P<file>[^:]+):[^:]+:(?P<label>.*)\s*$")

    targets = {}
    for line in fin:
        line = line.rstrip()
        mat = brk.match(line)
        if mat is not None:
            full_path = file_map[mat.group('file')]
            # print(f"match: {full_path}, {mat.group('label')}",
            #       file=sys.stderr)
            if full_path not in targets:
                targets[full_path] = scan_for_labels(full_path)
            linenum = targets[full_path][mat.group('label')]
            print(f'print "{mat.group("""label""")}"')
            print(f"break {mat.group('file')}:{linenum}")
        else:
            print(line)

def scan_for_labels(fname):
    "Return dict mapping labels to line numbers."
    label = re.compile(r"\s*case\s+(?P<label>TARGET[(][^)]+)[)]\s*:")
    linenums = {}
    # print(f"scanning {fname} for labels", file=sys.stderr)
    with open(fname) as inp:
        n = 0
        for line in inp:
            n += 1
            mat = label.match(line)
            if mat is not None:
                target = mat.group('label').replace("(", "_")
                linenums[target] = n
    return linenums

def find_source_files(pat="**/*.[ch]"):
    "From the current working directory, locate all .c and .h files."
    file_map = {}
    for full_path in glob.glob(pat, recursive=True):
        base = os.path.basename(full_path)
        # if base in file_map:
        #     print(f"Warning: {base} is file_map, refers to"
        #           f" {file_map[base]}, replace with {full_path}",
        #           file=sys.stderr)
        file_map[base] = full_path
    return file_map

if __name__ == "__main__":
    sys.exit(main())
