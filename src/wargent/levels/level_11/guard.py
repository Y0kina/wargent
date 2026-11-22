"""Guard for level 11.

accept_delegation(message, ctx) is called by the worker before it processes a delegated request.
message.text holds the request and message.source the sender. Return True to accept it.
The parser used by the agent is available:

    from wargent.engine.directives import parse
    parse(text).directives  ->  each directive has .sources, a list of (kind, value) pairs
"""


def accept_delegation(message, ctx):
    return True
