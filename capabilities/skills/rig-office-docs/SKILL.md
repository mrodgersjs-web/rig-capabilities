---
name: rig-office-docs
description: Create, read, and edit Office documents (docx, pptx, xlsx) and PDFs (create via reportlab, extract via pypdf) using the RIG office venv. Use when asked to generate or modify Word, PowerPoint, Excel, or PDF artifacts.
license: MIT
tags: [office, docx, pptx, xlsx, pdf, documents, reports, python]
owner: rig-intelligence
domain: Document production
status: Stable
verified_by: jake
verified_on: 2026-08-30
acl: [public]
outcome: docs-knowledge: Create, read, and edit Office documents (docx, pptx, xlsx) and PDFs (create via reportlab, extract via pypdf) using the
done_when:
  - file:capabilities/skills/rig-office-docs/SKILL.md
  - grep:capabilities/skills/rig-office-docs/SKILL.md:Office
great_example: examples/great/docs-knowledge/rig-office-docs.md
quality_floor: 0.6
---

# rig-office-docs

Clean-room office-document skill. Written from library documentation only; no
text is reproduced from any third-party skill.

## Interpreter rule (mandatory)

Never use system python or `pip install` into it. Every invocation goes through
the dedicated venv by absolute path:

```
/Users/rig128gb/Developer/rig-capabilities/.venvs/office/bin/python
```

Installed there: `python-docx`, `python-pptx`, `openpyxl`, `reportlab`, `pypdf`.
If that path is missing, rebuild with:

```
python3 -m venv /Users/rig128gb/Developer/rig-capabilities/.venvs/office && \
/Users/rig128gb/Developer/rig-capabilities/.venvs/office/bin/pip install python-docx python-pptx openpyxl reportlab pypdf
```

Scripts live beside this file in `scripts/`. Prefer the scripts for generation;
drop to inline `-c` / temp-file python (with the same interpreter) for anything
the scripts do not cover.

## DOCX (python-docx)

### Create

```
<VENV_PY> <SKILL_DIR>/scripts/make_docx.py /tmp/job/spec-docx.json
```

`make_docx.py spec` — top-level object:

| key | meaning |
|---|---|
| `path` | output `.docx` path (relative paths resolve against the spec file's directory) |
| `template` | optional existing `.docx` to use as the base document |
| `elements` | ordered list of elements below |

Element types:

- `{"type":"heading","text":"Title","level":1}` — Word Heading N style.
- `{"type":"paragraph","text":"Body","bold":false,"italic":false,"size_pt":11,"style":null}`
- `{"type":"list","items":["a","b"],"ordered":false}` — bullet or numbered list.
- `{"type":"table","rows":[["h1","h2"],["1","2"]],"header":true}` — first row bold when `header`; ragged rows padded with empty cells; `Table Grid` style.
- `{"type":"toc"}` — inserts a real Word TOC field (`TOC \o "1-3" \h \z \u`); Word refreshes it on open/field-update, so headless rendering shows the placeholder text, not entries.
- `{"type":"page_break"}`

### Read

```python
from docx import Document
doc = Document("in.docx")
for p in doc.paragraphs: ...          # p.text, p.style.name
for t in doc.tables:                  # t.rows[i].cells[j].text
```

### Edit

Open, mutate, save: `doc.add_heading/add_paragraph/add_table` append at the end;
insert by moving XML (`p._p.addnext(...)`), or edit `run.text` in place to keep
formatting. Save to a NEW path unless the user asked to overwrite.

### Tracked-changes caveat

`p.text` reflects only the accepted-visible stream: insertions (`w:ins`) appear
as normal text and deletions (`w:del`) are invisible, so you cannot tell what
was revised. Worse, editing paragraph text on a document with pending revisions
can silently accept or corrupt markup. For contract/legal docs that may carry
revisions, first enumerate
`doc.element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ins')`
(and `.../del`) and warn the user; for a true change-tracked workflow, surface
the document in Word rather than rewriting runs programmatically.

## PPTX (python-pptx)

### Create

```
<VENV_PY> <SKILL_DIR>/scripts/make_pptx.py /tmp/job/spec-pptx.json
```

`make_pptx.py spec`:

| key | meaning |
|---|---|
| `path` | output `.pptx` path (relative → spec dir) |
| `template` | optional base deck |
| `slides` | list of slide objects below |

Slide object keys:

- `title` — text for the title placeholder (idx 0).
- `layout` — explicit `slide_layouts` index; omitted picks 0 (title+subtitle), 1 (title+content) or 6 (blank) heuristically.
- `subtitle` — text for the body placeholder on title slides.
- `bullets` — list of `str` or `{"text":...,"level":N}`; written into the body placeholder's text frame (or an added textbox if the layout has none).
- `text` — plain body text (used only when `bullets` absent).
- `elements` — `[{"type":"table","rows":[[...]],"x_in":0.75,"y_in":1.6,"width_in":8,"height_in":2,"header":true}]`
- `notes` — speaker-notes text.

Layouts come from the (template's) `prs.slide_layouts`; index 5/6 are usually
Title-Only/Blank in the stock template. Read the layout name before assuming an
index when using a custom template. Text frames: one paragraph per bullet;
`para.level` sets indent depth. Tables are added as graphic frames positioned in
inches, not placeholders.

### Read/edit

```python
from pptx import Presentation
prs = Presentation("in.pptx")
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame: ...        # shape.text_frame.paragraphs
        if shape.has_table: ...             # shape.table.cell(r,c).text
```

Edit `run.text` in place to preserve fonts; `prs.save(new_path)`.

## XLSX (openpyxl)

### Create

```
<VENV_PY> <SKILL_DIR>/scripts/make_xlsx.py /tmp/job/spec-xlsx.json
```

`make_xlsx.py spec`:

| key | meaning |
|---|---|
| `path` | output `.xlsx` path (relative → spec dir) |
| `sheets` | list of sheet objects below |

Sheet object keys:

- `name` — sheet title (first sheet renames the default).
- `rows` — list of rows appended in order; any JSON scalars; strings starting with `=` are stored as live formulas (e.g. `"=SUM(B2:B9)"`). Formulas have no cached value until Excel recalculates — reopen with `load_workbook(path)` (formulas) or `load_workbook(path, data_only=True)` (cached values, empty in fresh files).
- `cells` — `{"C2": "=A2+B2"}` direct cell writes.
- `number_formats` — `{"B2:B10": "#,##0.00", "D2:D10": "0.0%"}` applied per range; use Excel format codes (currency `"$#,##0.00"`, date `"yyyy-mm-dd"`).
- `widths` — `{"A": 24}` column widths by letter.
- `freeze` — pane anchor, e.g. `"A2"` freezes row 1, `"B3"` freezes rows 1–2 and column A.
- `header_bold` — bold row 1.

### Read/edit

`load_workbook(path)` keeps formulas; `data_only=True` returns cached results
(`None` if never opened by Excel). Edit `ws["A1"] = ...`, save to a new path.

## PDF

### Create (reportlab platypus)

```
<VENV_PY> <SKILL_DIR>/scripts/make_pdf.py /tmp/job/spec-pdf.json
```

`make_pdf.py spec`:

| key | meaning |
|---|---|
| `path` | output `.pdf` path (relative → spec dir) |
| `title`, `author` | PDF metadata |
| `elements` | list below |

Element types: `heading` (`level` 1–2), `paragraph`, `bullets` (`items`),
`table` (`rows`, `header` — gridded, header row shaded and repeated across
page breaks), `page_break`, `spacer` (`height` pt). Data strings are
HTML-escaped, so `&<>` in content are safe. For finer layout, write inline
platypus code (SimpleDocTemplate + story) with the venv interpreter instead.

### Extract text (pypdf)

```python
from pypdf import PdfReader
r = PdfReader("in.pdf")
len(r.pages)                    # page count
t = "\n".join(p.extract_text() or "" for p in r.pages)
```

Extraction is layout-lossy for multi-column/scanned PDFs; image-only pages
yield empty strings (flag those to the user rather than claiming success).

## Verify every artifact

Reopen what you wrote with the same libraries before claiming done —
python-docx `Document(path)`, python-pptx `Presentation(path)`, openpyxl
`load_workbook(path)`, pypdf `PdfReader(path)` with `len(pages) > 0`. Report the
artifact size and the reopened counts.
