#!/usr/bin/env python

# Dispatch table used by InstructionSetConverter and its mixins
# pylint: disable=wrong-import-position
DISPATCH = {}

import rattlesnake.jump
import rattlesnake.binary
import rattlesnake.function
import rattlesnake.unary
import rattlesnake.forloop
import rattlesnake.loadstore
import rattlesnake.attributes
import rattlesnake.sequence
import rattlesnake.compare
