# Sub-skill: enhanced conversions and offline imports

1. Turn on enhanced conversions (web) and confirm in Diagnostics that it is recording, not just enabled.
2. Capture the Google Click ID (gclid) into the CRM on every lead form and call-tracking record; without it, offline import is impossible.
3. Define the offline stage worth importing (qualified lead, closed sale) and its timestamp rule (conversion time = the event date, not the import date).
4. Import on a schedule or via API; test with one manual upload first and watch it appear against the right clicks.
5. Keep the loop honest: if only 10% of leads get a CRM outcome recorded, the smart bidding signal is 90% noise - fix the CRM hygiene before scaling spend.
6. Document the data flow in `tracking-plan.md`: click -> lead -> CRM stage -> import, with owners at each hop.
