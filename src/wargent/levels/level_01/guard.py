"""Guard for level 1.

filter_output(text, ctx) receives the final reply before it is shown. ctx.secrets lists the
values the agent must protect. Return the text to display.
"""


def filter_output(text, ctx):
    return text
