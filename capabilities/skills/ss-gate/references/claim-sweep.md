# Sub-skill: claim sweep

1. Extract every number, percentage, dollar figure, client name and "I built / I did" claim from the artifact.
2. For each, write the source: a dated receipt, a URL, or "Mike's own claim, needs his confirmation".
3. Search the publication's other posts for the same figure (use the drafts API: `/api/v1/post_management/published` then `/api/v1/drafts/<id>`). Different figures for the same fact = contradiction.
4. Illustrative examples (a salon, a hypothetical company) must be labelled as illustrative in the text.
5. Output a table: claim, source, status (sourced / needs Mike / contradiction / cut).
