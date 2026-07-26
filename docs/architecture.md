# Architecture

## Product boundary

StartBuilding defines a human-reviewed software delivery method. The coding-agent host supplies
model execution and tools, the target repository supplies architecture and validation policy, Git
supplies isolation and source history, and local files supply resumable workflow state.

StartBuilding does not provide a queue, background worker, database, scheduler, multi-user approval
system, remote execution service, or project-management UI.

## Plugin layout

```text
plugin.json                         Copilot and VS Code manifest
.plugin/plugin.json                 VS Code precedence manifest
.claude-plugin/plugin.json          Claude Code manifest
.claude-plugin/marketplace.json     Self-hosted Claude catalog
skills/deliver/                     Shared workflow and artifact contract
copilot-agents/                     Copilot-native agent definitions
agents/                             Claude-native agent definitions
scripts/validate.sh                 Static validation entry point
```

The manifests share the stable `startbuilding` identity and `skills/` tree. The `.plugin` copy has
higher VS Code precedence and prevents a colocated Claude marketplace catalog from causing a direct
source installation to load Claude-format agents. The manifests select separate agent definitions
because host-native tool names, visibility controls, and delegation allowlists differ. Specialist
bodies remain identical so behavior does not drift while frontmatter preserves the strongest native
restriction each host supports.

## Components

The `deliver` skill is the canonical user entry point. It runs in the parent context, owns run
artifacts, selects the next state transition, and invokes one specialist at a time.

| Role | Responsibility | Copilot tools | Claude tools |
| --- | --- | --- | --- |
| Coordinator | State and delegation | read, search, edit, execute, agent | Read, Glob, Grep, Write, Edit, Bash, Agent allowlist |
| Planner | Repository research and plan | read, search | Read, Glob, Grep |
| Implementer | Approved edits and validation | read, search, edit, execute | Read, Glob, Grep, Edit, Write, Bash |
| Reviewer | Independent diff review | read, search, execute | Read, Glob, Grep, Bash |
| Committer | Staging, commit, push, and PR | read, execute | Read, Glob, Grep, Bash |

The Coordinator is also available as an explicit agent entry point. Specialists are hidden from the
normal Copilot picker but remain model-invocable. Claude plugin agents remain addressable by their
scoped names.

## State machine

```text
planning
  -> plan_review
  -> implementation
  -> implementation_blocked | automated_review
  -> changes_requested | review_approval
  -> delivered | delivery_blocked
```

The transition out of `plan_review` requires explicit user approval of the current plan. The
transition out of `review_approval` requires explicit user approval of the current review and a
delivery request. The turn that creates either artifact stops at its gate.

Every approval records the artifact path, its Git object hash, UTC time, and short approval text.
The hash is recomputed immediately before gated work. Editing or replacing the artifact invalidates
approval.

## Delivery scope

The Implementer reports repository-relative `implementationPaths`. The Reviewer examines the whole
working-tree diff and reports the subset of those paths it actually reviewed. The Committer stages
each reviewed implementation path explicitly and compares the staged diff with that scope.

This design allows unrelated pre-existing changes to remain in the working tree without silently
including them in the pull request. Ambiguous, protected, secret-bearing, or unreviewed paths block
delivery.

## Trust model

The primary controls are native tool allowlists, isolated specialist contexts, artifact-bound human
approval, and explicit Git path staging. Instructions reinforce those controls but do not replace
them.

StartBuilding intentionally ships no hooks or executable plugin runtime. The only bundled
executable is a contributor-facing static validator. Target-repository commands run through the
host's normal permission model, and Git hooks are never bypassed.

Plugin components have the lowest precedence when a project or user defines the same agent or skill
ID. Testers must inspect component source paths so a stale customization cannot masquerade as the
installed plugin.

## Versioning

Releases use semantic versioning. The version must match in all three plugin manifests and the
self-hosted catalog. Because clients cache explicit versions, every published behavior change
requires a version bump and changelog entry.
