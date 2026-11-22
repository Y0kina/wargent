"""Guard for level 10.

allow_memory_write(entry, source, ctx) is called before the agent stores an entry in its memory.
entry is the text to store and source is the role of the context that requested the write
(for example "user" or "document"). Return True to allow the write.
"""


def allow_memory_write(entry, source, ctx):
    return True
