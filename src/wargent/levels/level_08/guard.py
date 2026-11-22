"""Guard for level 8.

approve_tool_update(old, new, ctx) is called when the description of an approved tool differs
from the approved one. old and new are the two descriptions. Return True to accept the change.
"""


def approve_tool_update(old, new, ctx):
    return True
