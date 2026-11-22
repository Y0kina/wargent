"""Guard for level 4.

filter_segment(segment, ctx) is called for every piece of context before the agent reads it.
For web pages, segment.text holds the raw HTML. Segment fields: role, source, text, trusted.
Return the segment (optionally modified) or None to drop it. The agent never obeys instructions
found in a segment whose trusted field is False.
"""


def filter_segment(segment, ctx):
    return segment
