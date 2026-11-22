"""Guard for level 6.

allow_tool_call(call, ctx) is called before every tool call. For read_file, call.args["path"]
holds the requested path. Return True to allow the call. The fake file system decodes
percent-encoded characters and resolves "." and ".." segments before reading.
"""

ALLOWED_ROOT = "/docs/"


def allow_tool_call(call, ctx):
    if call.name == "read_file":
        return call.args["path"].startswith(ALLOWED_ROOT)
    return True
