#!/usr/bin/env python

# Dispatch table used by InstructionSetConverter and its mixins
# pylint: disable=wrong-import-position
DISPATCH = {}

from . import jump
from . import binary
from . import function
from . import unary
from . import forloop
from . import loadstore
from . import attributes
from . import sequence
from . import compare
from . import misc
from . import stack
