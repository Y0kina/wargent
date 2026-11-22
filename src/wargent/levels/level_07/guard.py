"""Guard for level 7.

filter_output(text, ctx) receives the final reply before the client renders it.
ctx.allowed_domains lists the approved image hosts. Markdown images have the form
![alt](url). Return the text to display.
"""


def filter_output(text, ctx):
    return text
