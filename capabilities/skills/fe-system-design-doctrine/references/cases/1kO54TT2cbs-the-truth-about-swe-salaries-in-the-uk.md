# Case: The truth about SWE salaries in the UK

Source: https://www.youtube.com/watch?v=1kO54TT2cbs (video id 1kO54TT2cbs). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video 1kO54TT2cbs against the local transcript.

- published 2022-05-27 / duration 853s (14:13) / problem type: career

## Author's framework as used
1. Frame the market before giving numbers: model the software job market as three compensation spikes (company tiers), not one average. CLAIM(1kO54TT2cbs@01:39) CLAIM(1kO54TT2cbs@02:03)
2. Define the experience levels by scope and independence (junior, middle, senior, staff) so the salary table has consistent rows. CLAIM(1kO54TT2cbs@03:47)
3. Fill the table tier by tier, level by level, in pounds. CLAIM(1kO54TT2cbs@05:04)
4. Add the market's shape: how the job postings distribute across tiers. CLAIM(1kO54TT2cbs@09:37)
5. Validate the table against first-hand recent offer numbers, then draw the negotiation conclusion. CLAIM(1kO54TT2cbs@10:43) CLAIM(1kO54TT2cbs@12:22)

## Worked design
There is no design case; the worked object is the compensation model. Dimensions below map to what is covered.

Requirements (scope of the analysis)
- Audience: engineers planning a move to the UK and researching realistic numbers, any specialization. CLAIM(1kO54TT2cbs@00:13) CLAIM(1kO54TT2cbs@00:24)
- The claim under test: that US-level salaries are achievable in the UK, against the common belief that UK pay is much lower. CLAIM(1kO54TT2cbs@00:43) CLAIM(1kO54TT2cbs@00:49)

Components (the market model)
- Y-axis: number of positions; X-axis: compensation; three spikes, one per company tier. CLAIM(1kO54TT2cbs@01:30)
- Tier determined by company size and earnings. CLAIM(1kO54TT2cbs@01:53)

Data model (levels)
- Junior: new graduates or no prior industry experience, need senior mentoring, paid near minimum wage at tier 1. CLAIM(1kO54TT2cbs@03:50)
- Middle: 2-5 years, handles complex features independently. CLAIM(1kO54TT2cbs@04:09)
- Senior: 5+ years, leads feature/product development, mentors juniors, key architecture role. CLAIM(1kO54TT2cbs@04:16)
- Staff: leads products' development, sets guidelines and direction across teams, business-aware; archetypes include tech lead and the fixer dropped onto fires. CLAIM(1kO54TT2cbs@04:34)

API / realtime / performance / accessibility, not covered.

Level-definition caveat he states
- He could find no tier 1 staff data point, because small companies typically have seniors do that work and may have no staff-level role at all. CLAIM(1kO54TT2cbs@05:53)

## Trade-offs he names
- Tier 1 vs tier 2 vs tier 3 as career choices: tier 1 buys simpler interviews and better work-life balance at low pay; tier 2 roughly doubles the money; tier 3 pays the most but competes for talent only among itself. CLAIM(1kO54TT2cbs@02:12) CLAIM(1kO54TT2cbs@06:28) CLAIM(1kO54TT2cbs@03:33)
- Researching the market vs accepting the first number: the same senior title spans 175K to 300K GBP in his offer sample, so research and multiple offers are the levers. CLAIM(1kO54TT2cbs@12:22)
- Convert currencies before comparing: his figures are in pounds, so dollar comparisons need conversion first. CLAIM(1kO54TT2cbs@05:24)

## Anti-patterns he warns about
- Believing the blanket myth that UK pay is always far below US pay and never testing it against tier-3 data. CLAIM(1kO54TT2cbs@00:49)
- Accepting an offer without knowing the tier bands, his example is a 10-year engineer starting at 60-80K GBP in London and complaining about money. CLAIM(1kO54TT2cbs@13:04)
- Interviewing at one company at a time, which leaves you no competing offer to negotiate with. CLAIM(1kO54TT2cbs@12:36)

## Dated / contestable
- Every figure is 2022 London, in GBP, and the tech hiring market shifted notably after that; treat the table as a shape, not a current quote. CLAIM(1kO54TT2cbs@05:04)
- The offer numbers are first-hand but second-hand to the viewer ("trust me" sourcing from friends and personal research) with no verifiable receipts attached. CLAIM(1kO54TT2cbs@10:21) CLAIM(1kO54TT2cbs@10:32)
- The 60/30/10 posting distribution is given without a source. CLAIM(1kO54TT2cbs@09:37)
- His estimate that 270K GBP is "about 350,000 dollars" reflects the 2022 exchange rate. CLAIM(1kO54TT2cbs@08:38)
- Whether UK senior comp genuinely reaches US levels depends heavily on the company and the year; his claim is plausible for tier 3 but not general. CLAIM(1kO54TT2cbs@00:43)
