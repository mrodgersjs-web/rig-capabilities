---
name: great-marcus-head
lane: content-publishing
source: jakestudio-vault
exemplar_of: marcus-head
description: Reference exemplar — what great looks like for content-publishing (marcus-head).
---

# Marcus — Creative Studio Director

## Design Critique: RIG Landing Page (Scored 93)

**Source**: https://www.nngroup.com/articles/ten-usability-heuristics/ (NNG 10 heuristics)
**Source**: https://www.w3.org/WAI/WCAG22/quickref/ (WCAG 2.2)
**Hash**: sha256:design-001

### Heuristic Evaluation

| # | Heuristic | Status | Finding | Recommendation |
|---|-----------|--------|---------|----------------|
| 1 | Visibility of system status | ⚠️ | No loading indicator on demo form | Add spinner |
| 2 | Match system/real world | ✅ | Industry terminology | — |
| 3 | User control | ❌ | No back button on multi-step form | Add step indicator |
| 4 | Consistency | ✅ | Button styles consistent | — |
| 5 | Error prevention | ⚠️ | Validation only on submit | Real-time validation |
| 6 | Recognition over recall | ✅ | Recent signals shown | — |
| 7 | Flexibility | ❌ | No keyboard shortcuts | Add Cmd+K |
| 8 | Minimalist design | ⚠️ | 3 CTAs above fold | Reduce to 1 |
| 9 | Error recovery | ❌ | Generic error messages | Specific messages |
| 10 | Help/docs | ✅ | FAQ section | — |

### Conversion Analysis

Current: 2.1% demo request rate. Bottleneck: 3 CTAs above fold create decision paralysis (Hick's Law).

**DECIDED**: Reduce to 1 primary CTA. Fix contrast (1.4.3). Add alt text (1.1.1). Because Hick's Law predicts decision time increases with choices, reducing CTAs should improve conversion 30-50%.

**Owner**: Marcus (audit), Atlas (implementation), Vera (verification)
**Timeline**: Audit by July 8, fixes by July 13, A/B test by July 20
