from __future__ import annotations

from markdown_it import MarkdownIt

md = MarkdownIt()


def extract_tasks(md_text: str) -> list[tuple[str, int]]:
    tokens = md.parse(md_text)
    tasks: list[tuple[str, int]] = []
    for i, t in enumerate(tokens):
        if t.type == "inline" and t.content.strip().startswith(("- [ ]", "- [x]", "- [X]")):
            line = t.content.strip()
            open_box = line.startswith("- [ ]")
            if open_box:
                tasks.append((line[5:].strip(), i))
    return tasks
