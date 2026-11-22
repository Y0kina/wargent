"""Guard for level 9.

allow_tool_call(call, ctx) is called before every tool call. call.name and call.args describe
the call. ctx.history lists the calls already allowed in the session and ctx.sensitive_prefixes
lists private path prefixes. Return True to allow the call.
"""

ALLOWED_TOOLS = {"read_file", "post_comment"}


def allow_tool_call(call, ctx):
    return call.name in ALLOWED_TOOLS
