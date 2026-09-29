# Component tree (S04 sub-skill)

Purpose: turn a mockup into a component tree and dependency graph whose leaves are small, whose owners are clear, and whose structure data flow can be planned against.

When to load: when you must draw or judge the component hierarchy of a page, feed, card system, or block-based editor.

## Step checklist

1. Sketch the mockup first; the tree comes from the mockup, not from imagination. CLAIM(5vyKhm2NTfw@06:21)
2. Draw the dependency graph right after: app root and router down to leaf components. That graph is what reveals data flow. CLAIM(3MADCVqL534@11:50) CLAIM(5vyKhm2NTfw@07:14)
3. Build from the smallest unit up (contact card first), then compose lists and views around it. CLAIM(LEaiGjffLEs@03:27)
4. Keep leaf components small: attach secondary actions (reply, copy, share, delete) behind one trigger instead of into the message component itself. CLAIM(LEaiGjffLEs@05:08)
5. Model interactive shells explicitly: hover reveals menu and dropdown, click opens a detail window. CLAIM(3MADCVqL534@10:20)
6. Keep simple content simple: a comment list with a show-more button plus an input, no media. CLAIM(3MADCVqL534@11:28)
7. Simplify component sizes for the interview (three pin sizes) even when production would have more. CLAIM(3MADCVqL534@09:25)
8. For product pages, draw the structural frame first: header (switcher, search, profile menu) over page content (promo, tagged card rows) plus footer. CLAIM(Tu-hZ6lqNtY@14:02)
9. Give rich cards explicit levels: base card, hover preview, full detail card with description, genres, cast, and episode list. CLAIM(Tu-hZ6lqNtY@12:35)
10. For block/component libraries, classify every component as visual, structural, or database-connectable so one shared interface covers the library. CLAIM(tsGarhpWOws@16:57)
11. Define a generic component-token type (typed props, plus a container variant holding a token list) so new components need no new plumbing. CLAIM(tsGarhpWOws@22:04)
12. Drive the parser from a syntax-spec table: a new component costs one rule and one render-function mapping. CLAIM(tsGarhpWOws@25:02)
13. For editable blocks, edit through contenteditable on the selected node only, and accept that no standard input events exist for it (observe DOM mutations). CLAIM(tsGarhpWOws@12:00)

## Laws for this sub-topic

- Dependency graph after the mockup, from app root to leaves. CLAIM(3MADCVqL534@11:50) CLAIM(5vyKhm2NTfw@07:14) consensus.
- Feed decomposition: story card plus comment list plus comment input, feed as the list wrapper. CLAIM(5vyKhm2NTfw@06:21) single-source.
- Pin as an interactive shell (hover menu/dropdown, click detail window). CLAIM(3MADCVqL534@10:20) single-source.
- Comment components structurally simple (list + show-more + input). CLAIM(3MADCVqL534@11:28) single-source.
- Interview-scale component sets (three sizes, not the production set). CLAIM(3MADCVqL534@09:25) single-source.
- Smallest-unit-first composition. CLAIM(LEaiGjffLEs@03:27) single-source.
- Secondary actions behind one trigger. CLAIM(LEaiGjffLEs@05:08) single-source.
- Page frame as header + page content + footer. CLAIM(Tu-hZ6lqNtY@14:02) single-source.
- Card levels: card, hover preview, full detail card. CLAIM(Tu-hZ6lqNtY@12:35) single-source.
- Component families: visual, structural, database-connectable. CLAIM(tsGarhpWOws@16:57) single-source.
- Generic component-token type with a container variant. CLAIM(tsGarhpWOws@22:04) single-source.
- Parser driven by a syntax-spec table (one rule + one render mapping per component). CLAIM(tsGarhpWOws@25:02) single-source.
- contenteditable on the selected node only. CLAIM(tsGarhpWOws@12:00) single-source.

## Decision table

| Tree question | Pick | When |
|---|---|---|
| Actions inside the leaf vs behind a trigger | Behind one trigger | More than one or two secondary actions per item. CLAIM(LEaiGjffLEs@05:08) |
| One card component with levels vs separate components | One component with named levels | Hover and detail share the same data. CLAIM(Tu-hZ6lqNtY@12:35) |
| N special-case blocks vs a family taxonomy | Family taxonomy (visual / structural / database) | An extendable block library. CLAIM(tsGarhpWOws@16:57) |
| Production-size variants vs interview-size | Interview-size | On the clock; say what you simplified. CLAIM(3MADCVqL534@09:25) |
| Comments embedded in the parent payload vs their own fetch | Own fetch | Keeps the parent entity small. CLAIM(3MADCVqL534@27:34) |

## Worked cases

- 3MADCVqL534 "Pinterest": pin shell, detail window, comment components, full app-root-to-leaf hierarchy.
- 5vyKhm2NTfw "Facebook News Feed": story card + comment list + input, NewsFeed as list wrapper.
- LEaiGjffLEs "Chat application": contact card first, then contact list and chat view.
- Tu-hZ6lqNtY "Netflix (product design)": page frame and the three-level movie card.
- tsGarhpWOws "Notion-like editor": component families, token type, syntax-spec-driven parser.
