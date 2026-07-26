---
name: deliver
description: "Run a human-in-the-loop software delivery workflow. Use when asked to plan and implement a work item, independently review changes, resume a StartBuilding run, or create a pull request after explicit approval."
argument-hint: "Work request, run directory, or explicit approval instruction"
user-invocable: true
disable-model-invocation: false
---

# StartBuilding Delivery

Coordinate repository-aware planning, implementation, independent review, and pull-request
delivery. Repository instructions are authoritative. Never infer approval or combine an approval
gate with the work that follows it.

Read the references when their subject becomes relevant:

- [Workflow stages](./references/workflow-stages.md) defines transitions, agent delegation, human
  gates, and blocked states.
- [Artifact contract](./references/artifact-contract.md) defines durable run state, revisions,
  content-bound approvals, and resume selection.
- [Project configuration](./references/project-configuration.md) defines optional repository policy
  and defaults.
- [Project configuration template](./assets/project.json) is an optional starting point for target
  repositories.

## Specialist agents

Use the exact native specialist supplied by this plugin. Never substitute a generic agent when a
named specialist is missing.

| Role | VS Code and Copilot | Claude Code |
| --- | --- | --- |
| Planner | `StartBuilding Planner` | `startbuilding:StartBuilding Planner` |
| Implementer | `StartBuilding Implementer` | `startbuilding:StartBuilding Implementer` |
| Reviewer | `StartBuilding Reviewer` | `startbuilding:StartBuilding Reviewer` |
| Committer | `StartBuilding Committer` | `startbuilding:StartBuilding Committer` |

The parent context owns orchestration and writes only workflow artifacts. Persist each specialist's
returned report exactly before changing `state.json`. The parent must not perform specialist work
when the matching agent is available.

## Non-negotiable rules

- Stop after creating or revising a plan. Implementation requires a later explicit approval.
- Stop after a review is ready. Commit, push, and pull-request work requires a later explicit
  approval of that exact review.
- Planner and reviewer roles are read-only. Implementers never deliver. Committers never edit
  source.
- Bind every approval to the current artifact path and Git object hash.
- Preserve unrelated user changes and exclude them from delivery.
- Never persist or stage credentials, tokens, environment files, secret values, or run artifacts.
- If native tool restrictions, required artifacts, or delivery prerequisites are unavailable, stop
  with a concrete blocker instead of weakening the workflow.
