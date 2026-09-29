---
name: layout-auto-layout
tier: sub
parent: ds-layout
---

# Layout Auto Layout

Purpose: nested groups, hug/fixed/fill, pins, wrap gaps, responsive rows, phone stack. Owns 44-47, 56, 57, plus the Figma rows in Tool-specific.

Load when: the task touches this part of layout and composition, or a ds-layout critique names it. Part of `ds-layout`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 44 | Build interface rows the way flexbox will build them: group related items, apply auto layout to each group, nest those groups into a row, then nest rows into a parent. Do not hand-drag list items into place. Auto layout is also how an 8 px spacing scale stays consistent. | Flux Academy, Jesse Showalter, DesignCourse | CLAIM(guYN5LaAcS8@01:04, guYN5LaAcS8@01:47, guYN5LaAcS8@02:43, 2UbxHkiPwxg@00:12, cf95Z7Ngg8k@09:29, QjK56pv9Qe4@02:43, QjK56pv9Qe4@04:06) | consensus | yes |
| 45 | Pixel padding plus fixed child widths does not respond when the frame shrinks. Set the parent to a fixed width with left and right constraints, set children from fixed to fill, and distribute the row (space-between, or fill) so the row tracks the parent. | Flux Academy, DesignCourse | CLAIM(guYN5LaAcS8@03:23, guYN5LaAcS8@03:36, guYN5LaAcS8@04:14, 2UbxHkiPwxg@20:24, QjK56pv9Qe4@02:58, QjK56pv9Qe4@03:16, QjK56pv9Qe4@04:16) | consensus | yes |
| 46 | Use hug when the frame must follow its content, fixed when you are setting the size, and fill when the child must follow the parent. A column that must stay aligned across rows gets a fixed width; the other columns fill what is left. | Flux Academy | CLAIM(2UbxHkiPwxg@05:20, 2UbxHkiPwxg@06:29, 2UbxHkiPwxg@07:43, 2UbxHkiPwxg@16:10) | single-source | yes |
| 47 | When items wrap, set the gap inside a line and the gap between lines separately. The worked demo used 20 px in the line and 40 px between lines. | Flux Academy | CLAIM(2UbxHkiPwxg@03:59, 2UbxHkiPwxg@04:47) | single-source | yes |
| 56 | Pin corner chrome before you resize: mark top-left, menu top-right. When the links no longer fit, swap the menu for a compact icon. Do not let either piece slide into the content. | DesignCourse | CLAIM(QjK56pv9Qe4@01:36, QjK56pv9Qe4@01:50, QjK56pv9Qe4@02:19) | single-source | no |
| 57 | Stop photos from stretching when the frame narrows: pin them to an edge or the center. At phone width, switch a horizontal card row to a vertical stack and reduce display type. Do not squeeze a three-up until the type overlaps. | DesignCourse | CLAIM(QjK56pv9Qe4@05:09, QjK56pv9Qe4@05:24, QjK56pv9Qe4@08:01, QjK56pv9Qe4@08:13, QjK56pv9Qe4@08:28) | single-source | no |

## Anti-patterns for this sub-topic
- Low-resolution or badly cut-out photos left in the layout. CLAIM(9eJYjNGeIOM@02:22)
- Hand-nudging a list instead of nesting auto-layout groups. CLAIM(guYN5LaAcS8@00:40)
