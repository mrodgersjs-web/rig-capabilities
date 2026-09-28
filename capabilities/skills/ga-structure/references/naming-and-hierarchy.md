# Sub-skill: naming and hierarchy

1. Adopt one convention everywhere: `<goal>-<geo>-<theme>-<type>` (example: `leads-denver-hvac-search`). Keep it lowercase, hyphen-delimited, no personal names.
2. Encode budget tier in the name only if budgets actually differ by tier; names describe mechanics, not hopes.
3. Use labels for everything soft (test status, funnel stage, priority, quarter): labels sort and filter without forcing a rename.
4. Document the convention at the top of `architecture.md`; future audits and scripts parse names.
5. Reconcile existing campaigns against the convention before building new ones; rename in one pass, and never rename mid-experiment (it destroys the readable history of the test).
6. Check that the convention survives export: no commas or pipes inside names.
