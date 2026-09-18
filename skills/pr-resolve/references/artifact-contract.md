# Run artifact contract

Store transient workflow state under `.startbuilding/runs/<work-id>/`. The work ID is derived from
the pull request number, such as `pr-42-resolve`. Add `.startbuilding/runs/` to the target
repository's `.gitignore` unless the team deliberately versions workflow evidence.

## Files

- `request.md`: the pull request identity, URL, branch names, and head SHA at intake.
- `diff.patch`: the pull request diff fetched at intake, exactly as the Planner reads it.
- `existing-comments.md`: the existing-comment snapshot fetched at intake, exactly as the Planner
  reads it.
- `plan.md`: exact initial Planner output, including the comment catalog.
- `implementation.md`: exact initial Implementer output.
- `delivery.md`: exact Committer result.
- `state.json`: machine-readable stage, pointers, plan approval, and posted reply IDs.

Never overwrite completed evidence. A repeated stage uses the next available numeric suffix, such
as `plan-2.md` or `implementation-2.md`, and updates the corresponding current pointer.

## State schema

Create state with this minimum shape and preserve unknown fields whenever it is updated:

```json
{
  "version": 1,
  "workId": "pr-42-resolve",
  "pullRequest": {
    "number": 42,
    "url": "https://github.com/example/example/pull/42",
    "headSha": "0000000000000000000000000000000000000000"
  },
  "stage": "intake",
  "currentPlan": null,
  "currentImplementation": null,
  "planApproval": null,
  "repliedCommentNumbers": [],
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

Timestamps use UTC RFC 3339 format. Paths are repository-relative, use forward slashes, and must
not traverse outside the repository.

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

Agent messages, silence, and approvals from another run never count as plan approval.

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
