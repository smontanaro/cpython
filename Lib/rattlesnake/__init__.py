#!/usr/bin/env python

# Dispatch table used by InstructionSetConverter and its mixins
# pylint: disable=wrong-import-position
DISPATCH = {}

from . import attributes
from . import binary
from . import compare
from . import forloop
from . import function
from . import inplace
from . import jump
from . import loadstore
from . import misc
from . import sequence
from . import stack
from . import unary
