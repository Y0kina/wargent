"""Guard for level 12.

Hooks:
  filter_segment(segment, ctx)  called for every piece of context; segment.text holds raw HTML
                                for web pages; return the segment or None.
  allow_tool_call(call, ctx)    called before every tool call; return True to allow.
  filter_output(text, ctx)      called on the final reply; ctx.allowed_domains lists approved hosts.
"""

import re
from urllib.parse import urlparse

ALLOWED_ROOT = "/docs/"
INTERNAL_DOMAIN = "corp.example.test"
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")


def filter_segment(segment, ctx):
    if segment.role == "web":
        return segment.with_text(COMMENT_RE.sub("", segment.text))
    return segment


def allow_tool_call(call, ctx):
    if call.name == "read_file":
        path = call.args["path"]
        return path.startswith(ALLOWED_ROOT) and ".." not in path
    if call.name == "send_email":
        return call.args["to"].endswith("@" + INTERNAL_DOMAIN)
    return True


def filter_output(text, ctx):
    def keep(match):
        host = urlparse(match.group(1)).hostname
        return match.group(0) if host in ctx.allowed_domains else "[image removed]"

    return IMAGE_RE.sub(keep, text)
