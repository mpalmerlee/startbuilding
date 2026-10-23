---
name: deliver
description: "Run a human-in-the-loop software delivery workflow. Use when asked to plan and implement a work item, independently review changes, resume a StartBuilding run, or create a draft pull request after explicit approval."
argument-hint: "Work request, run directory, or explicit approval instruction"
user-invocable: true
disable-model-invocation: false
---

# StartBuilding Delivery

Coordinate repository-aware planning, implementation, independent review, and pull-request
delivery. Repository instructions are authoritative. Never infer plan approval or combine the plan
gate with the implementation that follows it.

Read the references when their subject becomes relevant:

- [Workflow stages](./references/workflow-stages.md) defines transitions, agent delegation, human
  gates, and blocked states.
- [Artifact contract](./references/artifact-contract.md) defines durable run state, revisions, plan
  approval, and resume selection.
- [Project configuration](./references/project-configuration.md) defines optional repository policy
  and defaults.
- [Project configuration template](./assets/project.json) is an optional starting point for target
  repositories.

## Specialist agents

Each specialist is a native agent supplied by this plugin, named exactly as listed below. Look up
that exact name in the agent names your delegation tool accepts:

- If it lists `startbuilding:` followed by the exact name, such as
  `startbuilding:startbuilding-planner`, use that prefixed form.
- Otherwise, if it lists no agent name that starts with `startbuilding:`, and it lists the exact
  name, such as `startbuilding-planner`, use it.
- Otherwise, the specialist is unavailable. Stop with a concrete blocker that lists the agent
  names you found.

Match the whole name, never a part of it. Never substitute a generic agent or a differently
named agent, including a built-in agent such as `research`, `plan`, or `code-review`, or a
specialist of another StartBuilding skill.

| Role | Agent name |
| --- | --- |
| Planner | `startbuilding-planner` |
| Implementer | `startbuilding-implementer` |
| Reviewer | `startbuilding-reviewer` |
| Committer | `startbuilding-committer` |

The parent context owns orchestration and writes only workflow artifacts. Persist each specialist's
returned report exactly before changing `state.json`. The parent must not perform specialist work
when the matching agent is available.

## Non-negotiable rules

- Stop after creating or revising a plan. Implementation requires a later explicit approval.
- Stop after a review is ready. Commit, push, and pull-request work requires a later explicit
  delivery request.
- Planner and reviewer roles are read-only. Implementers never deliver. Committers never edit
  source.
- Record plan approval against the current plan artifact. A revised plan requires fresh approval.
- Preserve unrelated user changes and exclude them from delivery.
- Never persist or stage credentials, tokens, environment files, secret values, or run artifacts.
- If native tool restrictions, required artifacts, or delivery prerequisites are unavailable, stop
  with a concrete blocker instead of weakening the workflow.
