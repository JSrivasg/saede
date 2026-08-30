"""
Minimal Markdown renderer — just the subset the site's content actually uses.

Deliberately small and dependency-free rather than a full CommonMark
implementation. Supported:

  inline   **bold**, *italic*, [text](/link/), `code`
  block    # headings, - lists, 1. lists, > quotes, --- rules, paragraphs
  custom   :::medical ... ::: renders the "please see a doctor" call-out

If content ever needs more than this, that is a sign it should be a section
type in render.py instead.
"""
import html
import re

# --- inline ---------------------------------------------------------------

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITAL = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\*)")
_CODE = re.compile(r"`([^`]+)`")


def inline(text):
    """Escape the text, then re-introduce only the markup we allow."""
    if not text:
        return ""
    out = html.escape(str(text), quote=False)

    def link(m):
        label, href = m.group(1), m.group(2)
        # external links open in a new tab and carry rel for safety
        ext = href.startswith("http")
        attrs = ' target="_blank" rel="noopener noreferrer"' if ext else ""
        return '<a href="%s"%s>%s</a>' % (html.escape(href, quote=True), attrs, label)

    out = _LINK.sub(link, out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _ITAL.sub(r"<em>\1</em>", out)
    out = _CODE.sub(r"<code>\1</code>", out)
    return out


# --- blocks ---------------------------------------------------------------

def render(text):
    """Render a Markdown string to HTML."""
    lines = text.replace("\r\n", "\n").split("\n")
    out, i = [], 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # the medical call-out block
        if stripped.startswith(":::medical"):
            body, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith(":::"):
                body.append(lines[i])
                i += 1
            i += 1
            inner = render("\n".join(body))
            # the first heading inside becomes the call-out title
            out.append(
                '<aside class="medical-callout" role="note">'
                '<h3><span class="pearl" aria-hidden="true"></span>'
                "Please also see a doctor</h3>%s</aside>" % inner
            )
            continue

        if stripped.startswith("---"):
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            out.append("<h%d>%s</h%d>" % (min(level, 4), inline(stripped[level:].strip()), min(level, 4)))
            i += 1
            continue

        if stripped.startswith(">"):
            body = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                body.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(body)))
            continue

        if stripped.startswith(("- ", "* ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append("<li>%s</li>" % inline(lines[i].strip()[2:]))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue

        if re.match(r"^\d+\.\s", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                items.append("<li>%s</li>" % inline(re.sub(r"^\d+\.\s", "", lines[i].strip())))
                i += 1
            out.append("<ol>%s</ol>" % "".join(items))
            continue

        # paragraph — gather until a blank line or the start of another block
        body = []
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(
            ("#", "-", "*", ">", ":::", "---")
        ):
            body.append(lines[i].strip())
            i += 1
        if body:
            out.append("<p>%s</p>" % inline(" ".join(body)))
        else:
            i += 1

    return "\n".join(out)


# --- frontmatter ----------------------------------------------------------

def frontmatter(raw):
    """Split a '---' delimited YAML-ish frontmatter block from the body.

    Only handles `key: value` pairs, which is all the article files use.
    """
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    head, body = raw[3:end], raw[end + 4:]
    meta = {}
    for line in head.strip().split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"').strip("'")
        if v.isdigit():
            v = int(v)
        meta[k.strip()] = v
    return meta, body.strip()
