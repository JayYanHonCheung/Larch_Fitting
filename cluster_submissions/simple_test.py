# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import originpro as op


# Ensures that the Origin instance gets shut down properly.
import sys
def origin_shutdown_exception_hook(exctype, value, traceback):
    op.exit()
    sys.__excepthook__(exctype, value, traceback)
if op and op.oext:
    sys.excepthook = origin_shutdown_exception_hook


# Set Origin instance visibility.
if op.oext:
    op.set_show(True)

# YOUR CODE HERE

# Exit running instance of Origin.
if op.oext:
    op.exit()