"""Guard for level 2.

filter_segment(segment, ctx) is called for every piece of context before the agent reads it.
Segment fields: role, source, text, trusted. Return the segment (optionally modified with
segment.with_text(...) or dataclasses.replace) or None to drop it.
"""


def filter_segment(segment, ctx):
    return segment
