#!/usr/bin/env python
"""Render a .pdf artifact from a JSON spec via reportlab platypus (clean-room, MIT).

Usage: make_pdf.py <spec.json>
Spec shape: see SKILL.md "make_pdf.py spec". Output path is spec["path"],
resolved relative to the directory containing the spec file.
Exit 0 and print the artifact path on success.
"""
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(name="DocHeading1", parent=ss["Heading1"], fontSize=18, spaceAfter=8))
    ss.add(ParagraphStyle(name="DocHeading2", parent=ss["Heading2"], fontSize=14, spaceAfter=6))
    return ss


def _escape(text):
    # Minimal guard so stray & <> in data do not break platypus mini-HTML.
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(spec, out_path):
    ss = _styles()
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=LETTER,
        title=spec.get("title", "Document"),
        author=spec.get("author", ""),
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    story = []
    for el in spec.get("elements", []):
        kind = el.get("type")
        if kind == "heading":
            style = "DocHeading1" if int(el.get("level", 1)) <= 1 else "DocHeading2"
            story.append(Paragraph(_escape(el.get("text", "")), ss[style]))
        elif kind == "paragraph":
            story.append(Paragraph(_escape(el.get("text", "")), ss["BodyText"]))
            story.append(Spacer(1, 6))
        elif kind == "bullets":
            items = [ListItem(Paragraph(_escape(i), ss["BodyText"])) for i in el.get("items", [])]
            story.append(ListFlowable(items, bulletType="bullet", start="•"))
            story.append(Spacer(1, 6))
        elif kind == "table":
            rows = [[_escape(c) if c is not None else "" for c in r] for r in el.get("rows", [])]
            if not rows:
                raise ValueError("table element needs a non-empty 'rows' list")
            table = Table(rows, repeatRows=1 if el.get("header", True) else 0)
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(table)
            story.append(Spacer(1, 10))
        elif kind == "page_break":
            story.append(PageBreak())
        elif kind == "spacer":
            story.append(Spacer(1, float(el.get("height", 12))))
        else:
            raise ValueError(f"unknown element type: {kind!r}")
    if not story:
        story.append(Paragraph("(empty document)", ss["BodyText"]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    return out_path


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    spec_path = Path(argv[1]).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = Path(spec["path"])
    if not out.is_absolute():
        out = spec_path.parent / out
    built = build(spec, out)
    print(f"pdf written: {built} ({built.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
