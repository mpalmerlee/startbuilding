# Architecture

## Product boundary

StartBuilding is a framework for human-reviewed agentic graphs. The coding-agent host supplies
model execution and tools, the target repository supplies architecture and validation policy, Git
supplies isolation and source history, and local files supply resumable workflow state. The
`deliver` graph applies this framework to software changes; the `research` graph applies it to
investigation and recommendation.

StartBuilding does not provide a queue, background worker, database, scheduler, multi-user approval
system, remote execution service, or project-management UI.

## Plugin layout

```text
plugin.json                         Copilot and VS Code manifest
.plugin/plugin.json                 VS Code precedence manifest
.claude-plugin/plugin.json          Claude Code manifest
.claude-plugin/marketplace.json     Self-hosted Claude catalog
skills/deliver/                     Shared workflow and artifact contract
skills/research/                    Shared research workflow and artifact contract
agents/                             Shared cross-client agent definitions
scripts/validate.sh                 Static validation entry point
```

The manifests share the stable `startbuilding` identity and `skills/` and `agents/` trees. Copilot
manifests explicitly select `agents/`; the metadata-only Claude manifest relies on conventional
component discovery. Each shared `.agent.md` allowlist contains Copilot aliases and Claude-native
tool names. Each host ignores unsupported names and retains its native least-privilege tools.

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
normal Copilot picker but remain model-invocable. Claude plugin agents use scoped display names such
as `startbuilding:startbuilding-implementer`.

## Research components

The `research` skill is a second, independent graph. It runs in the parent context, owns its own
run artifacts, and invokes one read-only specialist at a time.

| Role | Responsibility | Copilot tools | Claude tools |
| --- | --- | --- | --- |
| Research Coordinator | State and delegation | read, search, edit, execute, agent | Read, Glob, Grep, Write, Edit, Bash, Agent allowlist |
| Researcher | Evidence gathering | read, search, fetch | Read, Glob, Grep, WebSearch, WebFetch |
| Skeptic | Adversarial critique | read, search, fetch | Read, Glob, Grep, WebSearch, WebFetch |
| Merger | Recommendation synthesis | read, search | Read, Glob, Grep |

Every research specialist is read-only in both vocabularies: none can edit files or run commands.
The Researcher and Skeptic additionally reach the network, because much of the documentation a
research question depends on lives outside the repository. The Researcher fetches primary sources
and cites them; the Skeptic verifies those citations instead of trusting them. Copilot supplies
`fetch` but no built-in web search, so that host retrieves URLs without the search step. The Merger
stays local and reasons only over the persisted findings and critique. The Research Coordinator's
`Agent` allowlist names only the research specialists, keeping the two graphs isolated. Both skills share
the same manifests, static validator, and `.startbuilding/runs/` artifact conventions.

## State machine

```text
planning
  -> plan_review
  -> implementation
  -> implementation_blocked | automated_review
  -> changes_requested | delivery_confirmation
  -> delivered | delivery_blocked
```

The transition out of `plan_review` requires explicit user approval of the current plan. The
transition out of `delivery_confirmation` requires a later explicit delivery request. The turn
that creates either the plan or review stops before the gated work.

Plan approval records the current plan artifact, UTC time, and short approval text. Plans are never
overwritten; a revision creates a suffixed artifact and changes `currentPlan`, invalidating prior
approval. Delivery confirmation is an action request and is not stored as an approval record.

The `research` graph uses its own, independent state machine:

```text
intake
  -> researching
  -> critiquing
  -> synthesizing
  -> recommendation_review
  -> researching | completed
```

The transition out of `recommendation_review` requires an explicit human response. Revision returns
to the specific stage that needs to repeat rather than restarting the whole run.

## Delivery scope

The Implementer reports repository-relative `implementationPaths`. The Reviewer examines the whole
working-tree diff and reports the subset of those paths it actually reviewed. The Committer stages
each reviewed implementation path explicitly and compares the staged diff with that scope.

This design allows unrelated pre-existing changes to remain in the working tree without silently
including them in the pull request. Ambiguous, protected, secret-bearing, or unreviewed paths block
delivery.

## Trust model

The primary controls are native tool allowlists, isolated specialist contexts, current-plan human
approval, explicit delivery confirmation, and explicit Git path staging. Instructions reinforce
those controls but do not replace them.

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
