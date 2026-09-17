---
name: pr-review
description: "Review the open pull request for the current branch like a principal engineer, skip issues already flagged on the PR, and post approved findings as PR comments after explicit human approval."
argument-hint: "Optional run directory or explicit findings-approval instruction; defaults to the pull request for the current branch"
user-invocable: true
disable-model-invocation: false
---

# StartBuilding PR Review

Review the pull request matching the currently checked-out branch, avoid repeating anything already
raised on that PR, and post only human-approved findings back to GitHub with `gh`. Repository
instructions are authoritative. Never infer findings approval or combine that gate with posting.

Read the references when their subject becomes relevant:

- [Workflow stages](./references/workflow-stages.md) defines transitions, agent delegation, the
  human findings-approval gate, and blocked states.
- [Artifact contract](./references/artifact-contract.md) defines durable run state, revisions, and
  resume selection.

## Specialist agents

Use the exact native specialist supplied by this plugin. Never substitute a generic agent when a
named specialist is missing.

| Role | VS Code and Copilot | Claude Code |
| --- | --- | --- |
| Reviewer | `startbuilding-pr-reviewer` | `startbuilding:startbuilding-pr-reviewer` |
| Commenter | `startbuilding-pr-commenter` | `startbuilding:startbuilding-pr-commenter` |

The parent context owns orchestration and writes only workflow artifacts. Persist each specialist's
returned report exactly before changing `state.json`. The parent must not perform specialist work
when the matching agent is available.

## Non-negotiable rules

- Require an open pull request for the current branch before any other action. Never search for or
  guess a different PR.
- The Reviewer is read-only: it must not edit files, stage changes, or call any mutating `gh` or
  Git command.
- Never report a finding that substantively repeats an existing PR comment or review thread,
  resolved or not.
- Stop after findings are ready and again before posting. Posting requires a later, explicit human
  approval naming which findings to post.
- Before posting, re-verify the pull request head has not moved since the findings were produced.
  Stop instead of posting against a stale diff.
- Never submit a review with an `APPROVE` or `REQUEST_CHANGES` event, merge the pull request, close
  it, or edit its title, description, or labels. Only `COMMENT` events and plain replies are
  allowed.
- Preserve unrelated user changes and exclude them from this run.
- Never persist or stage credentials, tokens, environment files, secret values, or run artifacts.
- If native tool restrictions, required artifacts, or `gh` prerequisites are unavailable, stop with
  a concrete blocker instead of weakening the workflow.
