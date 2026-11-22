"""Guard for level 5.

filter_segment(segment, ctx) is called for every piece of context before the agent reads it.
Tool descriptions have the role "tooldesc". Segment fields: role, source, text, trusted.
allow_tool_call(call, ctx) is called before every tool call. call.name and call.args describe
the call. Return True to allow it.
"""


def filter_segment(segment, ctx):
    return segment


def allow_tool_call(call, ctx):
    return True
