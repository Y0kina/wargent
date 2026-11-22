"""Guard for level 3.

filter_segment(segment, ctx) is called for every piece of context before the agent reads it.
Segment fields: role, source, text, trusted. The agent never obeys instructions found in a
segment whose trusted field is False. Use dataclasses.replace(segment, trusted=False) or return
None to drop the segment.
"""


def filter_segment(segment, ctx):
    return segment
