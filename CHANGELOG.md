# Changelog

All notable changes to StartBuilding are documented in this file.

## 0.6.0 - 2026-10-12

### Added

- Added the `/startbuilding:repo-pr-status` skill graph: takes a read-only snapshot of every open
  pull request in the current repository or a user-named `owner/name` (asking for one when the
  context is not a single GitHub repository), assigns each exactly one status with every matching
  reason tag and a suggested next action, and writes a local Markdown report
  (`intake -> collecting -> classifying -> reported | collection_blocked`, with an explicit
  reclassify loop that reuses the snapshot). It never makes a mutating `gh` call and has no
  approval gate.
- Added the status and tag model: eight statuses in precedence order (`possibly-obsolete`, `stale`,
  `draft`, `blocked`, `waiting-on-author`, `ready-to-merge`, `needs-review`, `unclassified`),
  driving and informational reason tags, and default thresholds of 14 days for `aging`, 30 days
  for `stale`, and 90 days for the time-only `abandoned` rule, overridable per repository in
  `.startbuilding/repo-pr-status.json` when run from the target repository's checkout.
  `blocked` includes approved pull requests waiting on CI
  (`awaiting-ci`) or on branch protection (`blocked-by-protection`), and unanswered reviewer
  comments drive `waiting-on-author`. Base-branch state, linked-issue state, comments, reviews,
  and review threads come from one read-only GraphQL `query` per pull request, which identifies
  bot authors by `__typename` so bot comments never count as reviewer feedback. One more read-only
  GraphQL `query` counts all open pull requests, so the report shows the true total and marks the
  snapshot truncated only when that total exceeds the listed pull requests. Comment, review, and
  thread-reply history beyond the fetched window is noted under Data gaps.
- Added new shared agents: `startbuilding-repo-pr-status-coordinator` and
  `startbuilding-repo-pr-status-analyst`. The Analyst has no shell, edit, or network access.
- Extended `scripts/validate.py` to validate the new skill graph, its agents and configuration
  asset, and the Coordinator's read-only `gh` markers, and to report missing agent files as errors.

## 0.5.0 - 2026-10-05

### Changed

- The `deliver` Committer now creates new pull requests as drafts with `gh pr create --draft`
  unless the delivery request explicitly asks for a ready-for-review pull request. It checks for
  an existing pull request with `gh pr view` before committing, only pushes to an existing pull
  request, never edits its title, body, or draft or ready state, and never runs `gh pr ready`. If
  draft creation fails, delivery blocks without retrying and reports the exact `gh pr create`
  command to run. A ready-for-review request against an existing draft delivers and reports the
  `gh pr ready` command to run.

## 0.4.0 - 2026-09-17

### Added

- Added the `/startbuilding:pr-review` skill graph: reviews the diff of the pull request matching
  the current branch like a principal engineer, skips findings that substantively repeat an
  existing PR comment, and posts only human-approved findings as a single `COMMENT`-event pull
  request review with `gh`
  (`intake -> reviewing -> findings_review -> posting -> posted | posting_blocked`).
- Added the `/startbuilding:pr-resolve` skill graph: catalogs and numbers every comment on the
  pull request matching the current branch, assigns each a category and recommendation, plans the
  needed fixes, implements them once approved, commits each planned group separately, pushes, and
  replies to every catalogued comment as appropriate
  (`intake -> cataloging -> plan_review -> implementation -> implementation_blocked | delivery -> delivered | delivery_blocked`).
- Added new shared agents: `startbuilding-pr-review-coordinator`, `startbuilding-pr-reviewer`,
  `startbuilding-pr-commenter`, `startbuilding-pr-resolve-coordinator`,
  `startbuilding-pr-resolve-planner`, `startbuilding-pr-resolve-implementer`, and
  `startbuilding-pr-resolve-committer` (seven agents total across the two new graphs). Every
  mutating agent in both graphs is restricted to plain comments and replies: neither graph can
  submit a review `APPROVE`/`REQUEST_CHANGES` event, merge a pull request, close it, or edit its
  title, description, or labels.
- Extended `scripts/validate.py` to validate the two new skill graphs and their full agent
  inventory alongside `deliver` and `research`.

## 0.3.1 - 2026-09-02

### Changed

- Gave the research Researcher and Skeptic web access (`fetch` for Copilot, `WebSearch` and
  `WebFetch` for Claude), because much of the documentation a research question depends on is
  external. The Researcher now cites each external source with its URL and retrieval date, and the
  Skeptic verifies those citations instead of trusting them. Both remain unable to edit files or run
  commands, and the Merger remains local-only.

## 0.3.0 - 2026-08-26

### Added

- Reframed StartBuilding as a plugin framework for human-in-the-loop agentic graphs, with
  `deliver` and `research` as its two current skill graphs.
- Added the `/startbuilding:research` skill graph: a read-only investigation and recommendation
  workflow with its own coordinator, artifact contract, and workflow stages
  (`intake -> researching -> critiquing -> synthesizing -> recommendation_review -> researching | completed`).
- Added four new shared agents: `startbuilding-research-coordinator`, `startbuilding-researcher`,
  `startbuilding-skeptic`, and `startbuilding-merger`. The three specialists are strictly read-only
  in both Copilot and Claude vocabularies.
- Generalized `scripts/validate.py` to validate every skill graph and its full agent inventory
  instead of a single hardcoded graph.

## 0.2.0 - 2026-07-26

### Changed

- Replaced Git-hash-bound plan approval with a lightweight current-plan artifact pointer.
- Replaced formal review approval records with a simple delivery confirmation after independent
  review.
- Limited default implementation validation to focused checks plus explicitly configured or
  repository-required commands, and directed reviewers to reuse existing results.
- Consolidated branch, secret, reviewed-path, staging, and GitHub checks at the Committer boundary.

## 0.1.2 - 2026-07-26

### Fixed

- Unified Copilot, VS Code, and Claude Code on one shared `agents/*.agent.md` inventory.
- Added dual-vocabulary tool allowlists so each host preserves native role boundaries while ignoring
  unsupported tool names.
- Made Copilot CLI installation the tested path for VS Code Agent Host discovery, eliminating the
  duplicate Claude-format agent set.

## 0.1.1 - 2026-07-26

### Fixed

- Added a higher-precedence VS Code manifest so direct source installations use the Copilot-native
  agents instead of treating the colocated Claude marketplace as the plugin format.
- Added delegated Planner and Implementer tool-availability checks to VS Code acceptance testing.

## 0.1.0 - 2026-07-26

### Added

- Shared `/startbuilding:deliver` workflow for planning, implementation, independent review, and
  pull-request delivery.
- Explicit plan and review approval gates bound to artifact content hashes.
- Durable, resumable local run artifacts under `.startbuilding/runs/`.
- Native least-privilege agent sets for VS Code, GitHub Copilot CLI, and Claude Code.
- Direct Git installation metadata and a self-hosted Claude plugin catalog.
- Static repository validation and cross-client acceptance guidance.
