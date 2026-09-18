# Architecture

## Product boundary

StartBuilding is a framework for human-reviewed agentic graphs. The coding-agent host supplies
model execution and tools, the target repository supplies architecture and validation policy, Git
supplies isolation and source history, and local files supply resumable workflow state. The
`deliver` graph applies this framework to software changes; the `research` graph applies it to
investigation and recommendation; the `pr-review` and `pr-resolve` graphs apply it to an already
open pull request, using `gh` as the interface to GitHub.

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
skills/pr-review/                   Shared PR review workflow and artifact contract
skills/pr-resolve/                  Shared PR feedback resolution workflow and artifact contract
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

## PR review components

The `pr-review` skill is a third, independent graph. It runs in the parent context, owns its own
run artifacts derived from the pull request number for the current branch, and invokes one
specialist at a time.

| Role | Responsibility | Copilot tools | Claude tools |
| --- | --- | --- | --- |
| PR Review Coordinator | State and delegation | read, search, edit, execute, agent | Read, Glob, Grep, Write, Edit, Bash, Agent allowlist |
| Reviewer | Diff review, dedup against existing comments | read, search, execute | Read, Glob, Grep, Bash |
| Commenter | Posts approved comments with `gh` | read, execute | Read, Glob, Grep, Bash |

The Reviewer is read-only even though it reaches `Bash`: its instructions restrict it to read-only
`gh` and `git diff` commands and forbid any command that comments, reviews, labels, merges, or
pushes. Only the Commenter may take that mutating action, and only after an explicit human
approval names which findings to post. The Commenter never submits an `APPROVE` or
`REQUEST_CHANGES` review event, so `pr-review` can never change a pull request's approval state.

## PR resolve components

The `pr-resolve` skill is a fourth, independent graph, structured like `deliver` but scoped to an
already open pull request's feedback instead of a fresh work request.

| Role | Responsibility | Copilot tools | Claude tools |
| --- | --- | --- | --- |
| PR Resolve Coordinator | State and delegation | read, search, edit, execute, agent | Read, Glob, Grep, Write, Edit, Bash, Agent allowlist |
| Planner | Catalogs every PR comment, categorizes it, and plans fixes | read, search, execute | Read, Glob, Grep, Bash |
| Implementer | Approved edits and validation | read, search, edit, execute | Read, Glob, Grep, Edit, Write, Bash |
| Committer | Grouped commits, push, and PR replies | read, execute | Read, Glob, Grep, Bash |

`pr-resolve` deliberately has no independent-review role: the human plan-approval gate is the only
gate before implementation, and the Committer delivers directly after implementation. Each
catalogued comment gets exactly one resolution recorded in the plan (fix now, reply-only, or no
action), and the Committer's replies must match: a commit reference for a fix, the plan's recorded
reasoning for an explicit no-fix decision, or no reply at all for a pure observation.

Both `pr-review` and `pr-resolve` are isolated from `deliver` and `research` and from each other,
following the same isolation principle as the research graph: each Coordinator's `Agent` allowlist
names only its own graph's specialists, so a mutating role from one graph can never be invoked as a
delegate of another.

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

The `pr-review` graph uses its own, independent state machine:

```text
intake
  -> reviewing
  -> findings_review
  -> posting
  -> posted | posting_blocked
  -> reviewing (revise findings)
```

The transition out of `findings_review` requires an explicit human approval naming which findings
to post. Before posting, the workflow re-checks the pull request's head SHA against the SHA
recorded when the findings were produced, and stops instead of posting against a moved head.

The `pr-resolve` graph uses its own, independent state machine:

```text
intake
  -> cataloging
  -> plan_review
  -> implementation
  -> implementation_blocked | delivery
  -> delivered | delivery_blocked
```

The transition out of `plan_review` requires explicit human approval of the current plan, recorded
the same way as `deliver`'s plan approval. There is no independent-review stage: implementation
transitions directly to delivery, which both delivers the approved changes and replies to the
pull request's comments.

## Delivery scope

The Implementer reports repository-relative `implementationPaths`. The Reviewer examines the whole
working-tree diff and reports the subset of those paths it actually reviewed. The Committer stages
each reviewed implementation path explicitly and compares the staged diff with that scope.

This design allows unrelated pre-existing changes to remain in the working tree without silently
including them in the pull request. Ambiguous, protected, secret-bearing, or unreviewed paths block
delivery.

`pr-resolve` applies the same staging discipline per commit group instead of once at the end: the
Committer stages and commits each of the plan's groups separately rather than staging all changes
together, then pushes once every group has landed.

## Trust model

The primary controls are native tool allowlists, isolated specialist contexts, current-plan human
approval, explicit delivery confirmation, and explicit Git path staging. Instructions reinforce
those controls but do not replace them.

`pr-review` and `pr-resolve` extend this model to GitHub mutation: both require `gh auth status` to
succeed before any mutating call, and both restrict every mutating agent to plain comments and
replies, never a review `APPROVE`/`REQUEST_CHANGES` event, a merge, a close, or an edit to the pull
request's title, description, or labels. `pr-review` additionally re-checks the pull request's head
SHA immediately before posting, so an inline comment can never be anchored to a diff position that
a later push has invalidated.

StartBuilding intentionally ships no hooks or executable plugin runtime. The only bundled
executable is a contributor-facing static validator. Target-repository commands run through the
host's normal permission model, and Git hooks are never bypassed.

Plugin components have the lowest precedence when a project or user defines the same agent or skill
ID. Testers must inspect component source paths so a stale customization cannot masquerade as the
installed plugin.

## Known limitations

Staging by path (`git add -- <path>`, used by the `deliver` and `pr-resolve` Committers) stages
that file's entire current diff, not only the hunks the approved plan or implementation produced.
If a file already has an unrelated, unstaged edit sitting in the working tree when StartBuilding
approves a change to that same file, `git add -- <path>` stages both together, and inspecting the
resulting staged diff does not distinguish an approved hunk from an unrelated one once they share a
file - both are just lines in the same staged diff.

This is not new to `pr-resolve`; `deliver`'s Committer has had the identical pattern since its
first release. It only became visible when `pr-resolve`'s multi-commit-group staging drew review
attention to the same instruction.

The documented mitigation today is procedural, not technical: avoid editing a file while a run is
actively working on it. A fix under consideration is to record, before a run starts touching a
path, whether that path already has uncommitted changes, and block staging and delivery for any
path where that overlap exists, rather than attempting hunk-level patch surgery. Blocking matches
the existing pattern used for protected paths, secrets, and unreviewed paths (see "Delivery
scope" above) more closely than trying to separate hunks would, at the cost of being coarser:
it would also block a same-file edit that does not actually overlap the approved hunks.

Every Coordinator's native tool allowlist (`Write`, `Edit`, `Bash`, plus its `Agent` allowlist) is
broader than its role. It legitimately needs `Write`/`Edit` to create and update run artifacts and
`Bash` to run precondition checks such as `git status`, `git branch`, or `gh auth status`, but
those same tools are also enough to edit source, commit, push, or post PR comments directly - the
mutating actions that are supposed to belong only to a delegated specialist. "Own only
orchestration... never perform specialist work" (see each Coordinator's instructions) is an
enforced boundary for every *specialist* role, whose own tool list has no `Bash`/`Edit`/`Write` to
misuse, but for the Coordinator itself it is a prose instruction, not a tool restriction.

A real fix would mean either giving the Coordinator a narrower, artifact-only write mechanism plus
a read-only-shaped `Bash` for precondition checks (so it has no path to source edits or mutating
Git/`gh` commands at all), or accepting that the trust model relies on instruction-following at
this one layer, same as the current design. No specific replacement tool exists yet; this is
recorded as a known gap rather than a planned change.

## Versioning

Releases use semantic versioning. The version must match in all three plugin manifests and the
self-hosted catalog. Because clients cache explicit versions, every published behavior change
requires a version bump and changelog entry.
