import re
from pathlib import Path

REPO = Path(__file__).resolve().parent
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s)\]]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(\S.*)$")
BULLET_RE = re.compile(r"^\s*[-*]\s")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
NUM_RE = re.compile(r"\d+(?:\.\d+)*")


def strip_comment(line):
    out, in_fence_marker = [], False
    for i, ch in enumerate(line):
        if ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).strip()


def annotated(md):
    res, in_fence = [], False
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            res.append((line, True))
            in_fence = not in_fence
            continue
        res.append((line, in_fence))
    return res


def sections(md):
    out = [{"level": 0, "title": "<preamble>", "prose": [], "code": []}]
    for line, fenced in annotated(md):
        m = HEADING_RE.match(line)
        if m and not fenced:
            out.append({"level": len(m.group(1)), "title": m.group(2).strip(), "prose": [], "code": []})
            continue
        out[-1]["code" if fenced else "prose"].append(line)
    return out


for name in ("README.md", "README.ja.md"):
    md = (REPO / name).read_text(encoding="utf-8")
    print("=====", name)
    for s in sections(md):
        prose = "\n".join(s["prose"])
        bullets = sum(1 for l in s["prose"] if BULLET_RE.match(l))
        links = len(MD_LINK_RE.findall(prose)) + len(URL_RE.findall(MD_LINK_RE.sub("", prose)))
        code = [strip_comment(l) for l in s["code"] if l.strip()]
        inline = INLINE_CODE_RE.findall(prose)
        nums = NUM_RE.findall(prose)
        print(f"  L{s['level']} {s['title']!r} bullets={bullets} links={links} nums={nums}")
        print(f"     code={code}")
        print(f"     inline={inline}")
