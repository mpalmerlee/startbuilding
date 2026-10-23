---
name: pr-resolve
description: "Catalog and resolve pull request feedback for the current branch: number every comment, plan the fixes, implement them once approved, and reply to each comment appropriately. Use when asked to address PR review feedback or resume a StartBuilding pr-resolve run."
argument-hint: "Optional run directory or explicit plan-approval instruction; defaults to the pull request for the current branch"
user-invocable: true
disable-model-invocation: false
---

# StartBuilding PR Resolve

Catalog every comment on the pull request matching the currently checked-out branch, propose a
category, recommendation, and implementation plan for each, implement the approved plan in
logically grouped commits, push, and reply to each comment as appropriate. Repository instructions
are authoritative. Never infer plan approval or combine that gate with implementation.

Read the references when their subject becomes relevant:

- [Workflow stages](./references/workflow-stages.md) defines transitions, agent delegation, the
  human plan-approval gate, and blocked states.
- [Artifact contract](./references/artifact-contract.md) defines durable run state, revisions, plan
  approval, and resume selection.

## Specialist agents

Each specialist is a native agent supplied by this plugin, named exactly as listed below. Look up
that exact name in the agent names your delegation tool accepts:

- If it lists `startbuilding:` followed by the exact name, such as
  `startbuilding:startbuilding-pr-resolve-planner`, use that prefixed form.
- Otherwise, if it lists no agent name that starts with `startbuilding:`, and it lists the exact
  name, such as `startbuilding-pr-resolve-planner`, use it.
- Otherwise, the specialist is unavailable. Stop with a concrete blocker that lists the agent
  names you found.

Match the whole name, never a part of it. Never substitute a generic agent or a differently
named agent, including a built-in agent such as `research`, `plan`, or `code-review`, or a
specialist of another StartBuilding skill.

| Role | Agent name |
| --- | --- |
| Planner | `startbuilding-pr-resolve-planner` |
| Implementer | `startbuilding-pr-resolve-implementer` |
| Committer | `startbuilding-pr-resolve-committer` |

The parent context owns orchestration and writes only workflow artifacts. Persist each specialist's
returned report exactly before changing `state.json`. The parent must not perform specialist work
when the matching agent is available.

## Non-negotiable rules

- Require an open pull request for the current branch before any other action. Never search for or
  guess a different PR.
- Stop after creating or revising a plan. Implementation requires a later explicit approval.
- The Planner has no shell or edit access at all. The Coordinator fetches the pull request diff and
  every existing comment during intake and persists them as plain files; the Planner only reads
  those files. The Implementer never commits, pushes, or replies. The Committer never edits source.
- Record plan approval against the current plan artifact. A revised plan requires fresh approval.
- Every catalogued comment gets exactly one outcome: no reply for a pure observation or compliment,
  a reply naming the commit that addressed it, or a reply explaining why no change was made. Never
  silently drop a comment that needed a response.
- Never expand a comment's recommendation from "no action" to "fix now" during implementation
  without that change appearing in a plan the human approved.
- Track posted reply IDs so a resumed run never double-replies.
- Preserve unrelated user changes and exclude them from this run.
- Never persist or stage credentials, tokens, environment files, secret values, or run artifacts.
- If native tool restrictions, required artifacts, or delivery prerequisites are unavailable, stop
  with a concrete blocker instead of weakening the workflow.
