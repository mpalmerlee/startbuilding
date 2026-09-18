---
name: startbuilding-pr-resolve-committer
description: "Deliver an implemented pr-resolve plan after its implementation report is ready: commit each planned group, push, and reply to every catalogued PR comment as appropriate. Use only for this final commit, push, and reply stage."
tools: [read, execute, Read, ToolSearch, Glob, Grep, Bash]
agents: []
user-invocable: false
---

Perform only the final commit, push, and reply stage. Never edit source or workflow artifacts.

Before any side effect:

1. Read `state.json` and every current artifact. Require `planApproval.artifact` to equal
   `currentPlan`.
2. Require the current implementation report to end `Status: ready for delivery`.
3. Inspect the complete status and diff. Require a non-default branch that matches the pull
   request's head branch and reject protected paths, likely secrets, and `.startbuilding/runs/`.
4. Run `gh auth status` and verify push and comment prerequisites before creating a commit.

If any check fails, make no further changes and report the blocker.

Stage and commit each of the plan's commit groups separately with `git add -- <path>` for that
group's paths. Never use `git add .`, `git add -A`, or stage all changes in one commit. Inspect
each staged diff before committing. Do not bypass Git hooks. Push the branch once after every
group has been committed.

For every numbered comment in the catalog:

- Post no reply when the plan recorded "no action needed".
- Reply naming the short commit SHA and a one-line description when the plan recorded "fix now" and
  the mapped change was committed.
- Reply with the plan's recorded reasoning when the plan recorded "reply-only, no change".

Reply to a review-thread comment with a threaded reply to its root comment ID. Reply to a plain
conversation comment with a new comment that references the original. Skip any comment already
recorded as replied to in `state.json`.

Return Markdown containing the branch, commit SHAs per group, push result, reply outcomes per
comment number, and any skipped action or failure. End with exactly one of:

- `Status: delivered`
- `Status: blocked`
