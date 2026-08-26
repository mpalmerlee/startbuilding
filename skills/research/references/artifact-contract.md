# Run artifact contract

Store transient workflow state under `.startbuilding/runs/<work-id>/`. The work ID must be a short,
lowercase, hyphenated identifier. Add `.startbuilding/runs/` to the target repository's
`.gitignore` unless the team deliberately versions workflow evidence.

## Files

- `request.md`: the original research question plus only clarifications relevant to the run.
- `findings.md`: exact initial Researcher output.
- `critique.md`: exact initial Skeptic output.
- `recommendation.md`: exact initial Merger output.
- `state.json`: machine-readable stage, pointers, and revision history.

Never overwrite completed evidence. A repeated stage uses the next available numeric suffix, such
as `findings-2.md`, `critique-2.md`, or `recommendation-2.md`, and updates the corresponding current
pointer.

## State schema

Create state with this minimum shape and preserve unknown fields whenever it is updated:

```json
{
  "version": 1,
  "workId": "short-work-id",
  "stage": "intake",
  "currentFindings": null,
  "currentCritique": null,
  "currentRecommendation": null,
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

Timestamps use UTC RFC 3339 format. Paths are repository-relative, use forward slashes, and must
not traverse outside the repository.

## Resume selection

1. If the user names a work ID or run directory, use only that run.
2. Otherwise inspect nonterminal runs.
3. If exactly one nonterminal run exists, present its path and current stage before resuming it.
4. If zero runs match, start a new run only when the user supplied a new research question.
5. If multiple runs match, list their work IDs and stages and ask the user to choose. Do not guess.

Read `request.md`, `state.json`, and every artifact named by a current pointer before selecting the
next transition.

## Data handling

Never store credentials, tokens, environment-file contents, secret values, or unrelated chat text.
Do not copy command output wholesale when a concise result is sufficient. Run state is local and
transient by default.
