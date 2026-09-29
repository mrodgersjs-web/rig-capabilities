---
name: form-input-design
tier: sub
parent: ds-ux
---

# Form Input Design

Purpose: field anatomy, states, error handling, and CTA emphasis.

Load when: the task touches this part of ux: flows, forms and accessibility, or a ds-ux critique names it. Part of `ds-ux`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 13 | Give every input a persistent visible label; a placeholder is never the label. | DesignCourse, Flux Academy | CLAIM(5-caRWzSQd4@04:02), CLAIM(EDtgsIn1meM@09:51) | consensus | yes |
| 14 | Name fields explicitly (First name, not Name) so the expected input is unambiguous. | DesignCourse | CLAIM(5-caRWzSQd4@04:12) | single-source | no |
| 15 | Design every form control as a component with named states: default, focus, typed, error. | DesignCourse | CLAIM(5-caRWzSQd4@00:20), CLAIM(EKjCC4PwjFo@09:02) | single-source | no |
| 16 | Show focus by darkening and thickening the field border (roughly 1px to 1.5px or 1px to 3px), not by other decoration. | DesignCourse | CLAIM(5-caRWzSQd4@14:34), CLAIM(EKjCC4PwjFo@11:14) | single-source | no |
| 17 | Give the field fill and border enough contrast to be perceived; when the fill is close to the page color, add a mid-gray stroke rather than leaving the field almost invisible. | DesignCourse | CLAIM(EKjCC4PwjFo@03:12), CLAIM(5-caRWzSQd4@06:27) | single-source | no |
| 18 | Size field height to a middle value with generous inner padding; never ship cramped or over-tall inputs. | DesignCourse | CLAIM(5-caRWzSQd4@05:42), CLAIM(EKjCC4PwjFo@04:52) | single-source | no |
| 19 | Keep one field aesthetic across the whole form: the same fill, stroke, and radius on text fields, text areas, checkboxes, selects, and buttons. | DesignCourse | CLAIM(5-caRWzSQd4@24:05) | single-source | no |
| 20 | Place error text directly under the failing field, not near the submit button. | DesignCourse | CLAIM(EKjCC4PwjFo@06:15) | single-source | no |
| 21 | Write error copy that states what happened in plain language and how to fix it, naming the rule that failed (for example a banned character), and color the failing field outline and its message with the error color so label, field, and message read as one problem. | NNgroup, DesignCourse | CLAIM(cCun-ReLTFI@00:41), CLAIM(5-caRWzSQd4@08:36), CLAIM(5-caRWzSQd4@09:32), CLAIM(EKjCC4PwjFo@07:06) | consensus | no |
| 22 | Put the fix inside the error message: a one-click remedy (removable filters, a corrected value) beats instructions the user must go apply elsewhere. | NNgroup | CLAIM(cCun-ReLTFI@01:06), CLAIM(cCun-ReLTFI@01:14) | single-source | no |
| 23 | Offer undo after any irreversible submit (sent message, placed order); it is the cheapest recovery path. | NNgroup | CLAIM(cCun-ReLTFI@01:34) | single-source | no |
| 24 | Set error and helper type no smaller than 14px, and keep label, value, and error text at three distinct hierarchy levels inside one field. | DesignCourse | CLAIM(5-caRWzSQd4@09:05), CLAIM(5-caRWzSQd4@07:20) | single-source | no |
| 25 | Make the form primary submit button the strongest-colored element in the form, using the theme primary color. | DesignCourse, Satori Graphics | CLAIM(5-caRWzSQd4@21:40), CLAIM(-5jSCHZIHlg@01:08) | consensus | yes |
| 26 | Change button hover by a subtle lightening only; a hover that flips background and text color is too large a jump. | DesignCourse | CLAIM(5-caRWzSQd4@23:13) | single-source | no |
| 27 | Constrain form fields to a readable column (one column centered, or a two-column split such as 60/40); never stretch inputs across the full screen width. | DesignCourse | CLAIM(EKjCC4PwjFo@21:30) | single-source | no |
| 28 | Mask password fields on entry, style the terms link as a link beside its checkbox, and give checkbox marks breathing room inside their box. | DesignCourse | CLAIM(EKjCC4PwjFo@19:18), CLAIM(EKjCC4PwjFo@21:10), CLAIM(EKjCC4PwjFo@20:30) | single-source | no |

## Anti-patterns for this sub-topic
- Mixed aesthetics between fields, checkboxes, and selects in one form (CLAIM(5-caRWzSQd4@24:05)).
- Full-screen-width text inputs (CLAIM(EKjCC4PwjFo@21:30)).
