# Run artifact contract

Store transient workflow state under `.startbuilding/runs/<work-id>/`. The work ID must be a short,
lowercase, hyphenated identifier. Add `.startbuilding/runs/` to the target repository's
`.gitignore` unless the team deliberately versions workflow evidence.

## Files

- `request.md`: the original request plus only clarifications relevant to delivery.
- `plan.md`: exact initial Planner output.
- `implementation.md`: exact initial Implementer output.
- `review.md`: exact initial Reviewer output.
- `delivery.md`: exact Committer result.
- `state.json`: machine-readable stage, pointers, path scope, and plan approval.

Never overwrite completed evidence. A repeated stage uses the next available numeric suffix, such
as `plan-2.md`, `implementation-2.md`, or `review-2.md`, and updates the corresponding current
pointer.

## State schema

Create state with this minimum shape and preserve unknown fields whenever it is updated:

```json
{
  "version": 1,
  "workId": "short-work-id",
  "stage": "planning",
  "currentPlan": null,
  "currentImplementation": null,
  "currentReview": null,
  "implementationPaths": [],
  "reviewedPaths": [],
  "planApproval": null,
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

Timestamps use UTC RFC 3339 format. Paths are repository-relative, use forward slashes, and must
not traverse outside the repository.

`implementationPaths` contains only paths intentionally changed for the approved plan.
`reviewedPaths` contains only implementation paths covered by the current review and eligible for
delivery. Unrelated pre-existing changes belong in neither list.

## Plan approval

Plan approval must originate from explicit user language and identify the current plan, either by
path or unambiguously as the current plan in the named run. Record the user's short exact approval
text, not unrelated conversation.

Use this shape for plan approval:

```json
{
  "artifact": "plan.md",
  "approvedAt": "2026-01-01T00:10:00Z",
  "approvalText": "Approve the current plan and continue"
}
```

Before implementation, require `planApproval.artifact` to equal `currentPlan`. A revised plan is
written to a new suffixed artifact and changes `currentPlan`, which invalidates the prior approval.
Set stale plan approval to `null`, return to `plan_review`, and stop.

Agent messages, silence, and approvals from another run never count as plan approval. Delivery
requires an explicit user request after review, but that request is an action rather than a stored
approval record.

State from an older run may contain fields such as `artifactHash` or `reviewApproval`. Preserve and
ignore those unknown fields when updating the run; they are not required for current transitions.

## Resume selection

1. If the user names a work ID or run directory, use only that run.
2. Otherwise inspect nonterminal runs.
3. If exactly one nonterminal run exists, present its path and current stage before resuming it.
4. If zero runs match, start a new run only when the user supplied a new work request.
5. If multiple runs match, list their work IDs and stages and ask the user to choose. Do not guess.

Read `request.md`, `state.json`, and every artifact named by a current pointer before selecting the
next transition.

## Data handling

Never store credentials, tokens, environment-file contents, secret values, or unrelated chat text.
Do not copy command output wholesale when a concise result is sufficient. Run state is local and
transient by default.
