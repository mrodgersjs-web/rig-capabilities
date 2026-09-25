# Great example - web-imagery

The SaaS pricing page rebrand for a fictional client "Northwind Billing", shipped as a
single 1440x900 hero plus four feature cards.

What makes it excellent:

1. Every asset carries a named role and none of them is decoration. The hero is a real
   product screenshot of the invoice-reconciliation view at 2400x1600 source, cropped
   16:9 with the totals column left in frame because that column IS the claim. Two
   feature cards use 4:3 crops of the same screenshot at different zoom, so the page
   reads as one product rather than three stock moods. The proof face is a real customer
   photograph, 1:1, shot against their own office wall.

2. Specificity ladder rung recorded per asset. Hero: rung 1 (real product screenshot).
   Feature cards: rung 1. Proof face: rung 2 (real customer photograph). The one
   illustration on the page, a 3-step onboarding diagram, is rung 4 and is labelled as
   a diagram so nobody mistakes it for a screenshot.

3. Grade and crop are consistent. All three photographs share one temperature (5600K),
   one contrast curve and a single 2% vignette, so the set reads as one shoot. Faces sit
   on the right third and look left, into the headline and the CTA.

4. Paint budget held. The hero is preloaded, AVIF at 2x with WebP and JPEG fallbacks,
   186KB delivered. The two card crops are lazy-loaded WebP at 54KB each. Total imagery
   weight on the page is 341KB against a 2MB page budget.

5. The record exists. assets/SOURCES.md has one row per asset with source URL, author,
   licence and version, retrieval date and release status. No row has an empty licence
   cell.

The result to beat: a stranger shown the page for five seconds answered "invoice
reconciliation for finance teams" and "click the orange button" without prompting, and
could not swap any image to a competitor's page without breaking a claim.
