# Run artifact contract

Store transient workflow state under `.startbuilding/runs/<work-id>/`. The work ID is derived from
the pull request number, such as `pr-42-review`. Add `.startbuilding/runs/` to the target
repository's `.gitignore` unless the team deliberately versions workflow evidence.

## Files

- `request.md`: the pull request identity, URL, branch names, and head SHA at intake.
- `diff.patch`: the pull request diff fetched at intake, exactly as the Reviewer reads it.
- `existing-comments.md`: the existing-comment snapshot fetched at intake, exactly as the Reviewer
  reads it.
- `findings.md`: exact initial Reviewer output.
- `posted.md`: exact Commenter result.
- `state.json`: machine-readable stage, pointers, approved posting scope, and posted comment IDs.

Never overwrite completed evidence. A repeated stage uses the next available numeric suffix, such
as `findings-2.md`, and updates the corresponding current pointer.

## State schema

Create state with this minimum shape and preserve unknown fields whenever it is updated:

```json
{
  "version": 1,
  "workId": "pr-42-review",
  "pullRequest": {
    "number": 42,
    "url": "https://github.com/example/example/pull/42",
    "headSha": "0000000000000000000000000000000000000000"
  },
  "stage": "intake",
  "currentFindings": null,
  "approvedFindings": null,
  "postedCommentIds": [],
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

Timestamps use UTC RFC 3339 format. Paths are repository-relative, use forward slashes, and must
not traverse outside the repository.

## Approved posting scope

Approval must originate from explicit user language and identify which findings to post, by number
or unambiguously as all findings in the current artifact. Record the exact approved set, including
any human edits to a finding's body or location, before posting. A revised findings artifact
invalidates any prior approved scope.

## Resume selection

1. If the user names a work ID or run directory, use only that run.
2. Otherwise inspect nonterminal runs whose recorded pull request matches the current branch.
3. If exactly one nonterminal run matches, present its path and current stage before resuming it.
4. If zero runs match, start a new run.
5. If multiple runs match, list their work IDs and stages and ask the user to choose. Do not guess.

Read `request.md`, `state.json`, and every artifact named by a current pointer before selecting the
next transition.

## Data handling

Never store credentials, tokens, environment-file contents, secret values, or unrelated chat text.
Do not copy command output wholesale when a concise result is sufficient. Run state is local and
transient by default.
