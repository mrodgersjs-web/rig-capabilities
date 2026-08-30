#!/usr/bin/env python
"""Render a .docx artifact from a JSON spec (clean-room, MIT).

Usage: make_docx.py <spec.json>
Spec shape: see SKILL.md "make_docx.py spec". Output path is spec["path"],
resolved relative to the directory containing the spec file.
Exit 0 and print the artifact path on success.
"""
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


def _add_toc(doc):
    """Insert a real Word TOC field (updates when Word opens/refreshes fields)."""
    para = doc.add_paragraph()
    run = para.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), r'TOC \o "1-3" \h \z \u')
    inner = OxmlElement("w:r")
    inner_text = OxmlElement("w:t")
    inner_text.text = "Right-click and choose Update Field to build the table of contents."
    inner.append(inner_text)
    fld.append(inner)
    para._p.append(fld)


def _add_table(doc, rows, header=True):
    if not rows:
        raise ValueError("table element needs a non-empty 'rows' list")
    n_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.style = "Table Grid"
    for i, row in enumerate(rows):
        for j in range(n_cols):
            value = row[j] if j < len(row) else ""
            cell_text = "" if value is None else str(value)
            cell = table.cell(i, j)
            cell.text = cell_text
            if header and i == 0:
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.bold = True
    return table


def _apply_run_style(run, el):
    run.bold = bool(el.get("bold", False))
    run.italic = bool(el.get("italic", False))
    size = el.get("size_pt")
    if size:
        run.font.size = Pt(float(size))


def build(spec, out_path):
    doc = Document(spec.get("template")) if spec.get("template") else Document()
    for el in spec.get("elements", []):
        kind = el.get("type")
        if kind == "heading":
            level = int(el.get("level", 1))
            doc.add_heading(el.get("text", ""), level=level)
        elif kind == "paragraph":
            p = doc.add_paragraph(style=el.get("style"))
            run = p.add_run(el.get("text", ""))
            _apply_run_style(run, el)
        elif kind == "list":
            style = "List Number" if el.get("ordered") else "List Bullet"
            for item in el.get("items", []):
                doc.add_paragraph(str(item), style=style)
        elif kind == "table":
            _add_table(doc, el.get("rows", []), header=bool(el.get("header", True)))
        elif kind == "toc":
            _add_toc(doc)
        elif kind == "page_break":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        else:
            raise ValueError(f"unknown element type: {kind!r}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
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
    print(f"docx written: {built} ({built.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
