# LinkedIn Groups: highest leverage, lowest cost

A group post is served to the group rather than lottery-tested against followers. Measured on a 10,036-follower account, a post reached 69 people in its first hour while four group posts put the same argument in front of roughly 102,000 members. Run groups first on every distribution day.

## Mechanics (read the mechanics file before every group post)

The group composer fails silently and has shipped title-only posts; an off-screen decoy editor was the root cause once. Read `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md` first, every time.

1. Open the source post, copy its URL.
2. Go to the group page and write group-specific copy. Never the LinkedIn text: identical copy in two groups is detectable cross-posting and fails the whole batch on a duplicate pair.
3. Only the visible editor persists; a second, off-screen editor at a negative x offset does not. Keep headlines to about 400 characters.
4. Put the LinkedIn post URL on the last line; that is what renders the preview card carrying the post's image, which is how the image gets in without fighting a file chooser.
5. Verify the body exists on the permalink after publishing. Title-only is a defect. A success toast is not evidence.
6. Public groups publish instantly; private groups go to moderation and are invisible to the author. Absence of a visible post is neither proof of rejection nor of success.

## Adapt by audience, not by template

| Group audience | Lead with |
|---|---|
| Lean / CI practitioners | the process gap, with a manufacturing example |
| HR / People ops | the engagement and retention angle |
| Innovation leaders | the program failure rate |
| Local / regional | the local connection or event |
| General business | the contrarian stat, short |

Five groups per sitting, different copy in each. Which groups the account is actually in is account state: check memberships before planning, never assume them from a list written last month.

## Route-back and gates

- The route-back for groups is the last line of the body (it renders the image card). Nowhere else.
- `route_back_compliance` and `adapt_not_copy` both run against the batch; a duplicate pair fails everything, not just the pair.
- A group post is outward and reversible, and runs under the batch approval Mike gave for the named groups and texts.
- Never post the same copy to two groups; LinkedIn can detect cross-posted content.

Absorbed from: linkedin-cross-platform, reddit-and-groups, lg-distribute.
