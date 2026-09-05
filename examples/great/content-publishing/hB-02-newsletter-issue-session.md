---
name: great-hB-02-newsletter-issue-session-yaml
lane: content-publishing
exemplar_of: hB-02-newsletter-issue-session.yaml
description: Reference exemplar for a segmented newsletter issue with a measurable promise, disciplined links, compliant twins, and rendering proof.
---

# hB-02-newsletter-issue-session.yaml — great example

## Input

Prepare a hybrid newsletter for a named subscriber segment and Mountain-time send window. The brief locks one promise and one primary link goal. Produce five subject candidates, a complementary preheader, a scannable issue, and matching plain-text version without performing a send.

## Output

The session produces `brief.yaml`, `subjects.txt` with winner and runner-up, `preview.txt`, `issue.md`, `issue.txt`, two reference-client renders, and a packet that records the winner subject. All outbound links are UTM-tagged and there are no more than seven.

```console
$ awk 'length($0)>50 { long=1 } NF { count++ } END { if (long || count<5) exit 1 }' "$SESS/subjects.txt"
# expected: exit 0 and at least five non-empty subject lines

$ python3 scripts/html_text_parity.py "$SESS/issue.md" "$SESS/issue.txt"
# expected: exit 0 with link_count_delta=0

$ sha256sum -c "$SESS/proof/packet.sha256"
# expected: issue, plain-text twin, and subjects match their sealed hashes
```

## Acceptance

- The body pays off the brief promise in its first 20% and returns to it in the final section.
- Paragraph/header rhythm passes the skeleton scan; every URL resolves and carries `utm_source`.
- Unsubscribe, mailing address, and permission reminder are present.
- Gmail and Apple Mail evidence exists (or equivalent DOM assertions), plain-text link parity is zero, and the issue remains unsent.
