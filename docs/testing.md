# Testing

## Static validation

From the repository root, run:

```sh
./scripts/validate.sh
claude plugin validate . --strict
```

The repository validator checks manifest identity and version parity, component paths, skill links,
project policy, the shared agent inventory, dual-vocabulary tool restrictions, coordinator
allowlists, stale identifiers, ASCII text, trailing whitespace, and executable permissions. It
excludes `.startbuilding/runs/`, since that tree holds transient, gitignored workflow evidence
rather than shipped plugin content.

## Prevent customization collisions

Personal and project agents or skills take precedence over plugin components. Before testing, inspect
`~/.copilot/agents/`, `~/.copilot/skills/`, `~/.claude/agents/`, and project customization folders.
Temporarily remove or rename earlier proof-of-concept copies whose IDs could shadow StartBuilding.

In every client, confirm the loaded component source points to this plugin rather than a personal or
project file.

## VS Code Agent Host test

1. Enable `chat.plugins.enabled` and the Agent Host, then select the Copilot harness.
2. Install the working tree through Copilot CLI so VS Code discovers the same package:

   ```sh
   copilot plugin install /absolute/path/to/startbuilding
   ```

3. Reload the VS Code window. Open **Chat: Open Customizations** and confirm the `deliver`,
   `research`, `pr-review`, `pr-resolve`, and `repo-pr-status` skills and exactly eighteen
   StartBuilding agents have no diagnostics or duplicate variants.
4. Confirm every agent source resolves through the shared `agents/` directory.
5. Invoke the Planner as a subagent and confirm it receives workspace read and file-search tools.
6. Invoke the Implementer as a subagent and confirm it receives filesystem, edit, and shell tools.
7. Confirm `/startbuilding:deliver` appears and the Coordinator can invoke each exact specialist.
8. Confirm `/startbuilding:research` appears and the Research Coordinator can invoke the
   Researcher, Skeptic, and Merger. Confirm the Merger receives only workspace read and
   file-search tools, and that the Researcher and Skeptic receive those plus web fetch, with no
   edit or shell tools for any of the three.
9. Confirm `/startbuilding:pr-review` appears and the PR Review Coordinator can invoke the
   Reviewer and Commenter. Confirm the Reviewer receives only workspace read and file-search
   tools, with no shell access at all, and that only the Commenter receives shell access (for
   `gh`), restricted by its own instructions to a `COMMENT`-event review.
10. Confirm `/startbuilding:pr-resolve` appears and the PR Resolve Coordinator can invoke the
    Planner, Implementer, and Committer, mirroring the `deliver` tool boundaries with no
    independent-review role.
11. Confirm `/startbuilding:repo-pr-status` appears and the Repo PR Status Coordinator can invoke
    only the Analyst. Confirm the Analyst receives only workspace read and file-search tools, with
    no shell, edit, or web access.
12. Disable the plugin and confirm its components disappear; enable it and confirm they return.

## Copilot CLI local test

Load the working tree for one session without changing persistent configuration:

```sh
copilot --plugin-dir /absolute/path/to/startbuilding plugin list
```

Confirm the output lists `startbuilding` under external plugins. After the repository is public,
exercise persistent lifecycle commands:

```sh
copilot plugin install mpalmerlee/startbuilding
copilot plugin list
copilot plugin disable startbuilding
copilot plugin enable startbuilding
copilot plugin update startbuilding
copilot plugin uninstall startbuilding
```

Confirm VS Code discovers the CLI-installed plugin and reports the expected source.

## Claude Code local test

Validate and load the working tree without installation:

```sh
claude plugin validate . --strict
claude --plugin-dir /absolute/path/to/startbuilding
```

Inside Claude Code, confirm `/startbuilding:deliver`, `/startbuilding:research`,
`/startbuilding:pr-review`, `/startbuilding:pr-resolve`, and `/startbuilding:repo-pr-status` are
available and plugin agents appear
under their scoped names, such as `startbuilding:startbuilding-implementer`. Confirm Planner gets
only `Read`, `Glob`, and `Grep`; Implementer gets `Read`, `Glob`, `Grep`, `Edit`, `Write`, and
`Bash`; and Coordinator gets `Read`, `Write`, `Edit`, `Bash`, and the scoped `Agent` allowlist.
Confirm the Researcher, Skeptic, and Merger each get only `Read`, `Glob`, and `Grep`, and that the
Research Coordinator's `Agent` allowlist names only those three.

Confirm the PR Reviewer gets only `Read`, `Glob`, and `Grep` (no `Bash`), the PR Commenter gets
those plus `Bash`, and the PR Review Coordinator's `Agent` allowlist names only those two. Confirm
the PR Resolve Planner gets only `Read`, `Glob`, and `Grep` (no `Bash`); the PR Resolve Implementer
gets those plus `Edit`, `Write`, and `Bash`; the PR Resolve Committer gets `Read`, `Glob`, `Grep`,
and `Bash`; and the PR Resolve Coordinator's `Agent` allowlist names only those three. Confirm the
Repo PR Status Analyst gets only `Read`, `Glob`, and `Grep` (no `Bash`), and the Repo PR Status
Coordinator's `Agent` allowlist names only the Analyst. Use `/reload-plugins` after changing
components.

Test persistent installation through the self-hosted catalog:

```sh
claude plugin marketplace add /absolute/path/to/startbuilding
claude plugin install startbuilding@startbuilding
claude plugin list
claude plugin disable startbuilding@startbuilding
claude plugin enable startbuilding@startbuilding
claude plugin uninstall startbuilding@startbuilding
```

Repeat with the public GitHub repository before release.

## Disposable repository

Use a small repository with a testable source file, a focused validation command, a Git remote you
control, and no valuable uncommitted work. Commit `AGENTS.md` with the validation command. Add:

```gitignore
.startbuilding/runs/
```

Configure `gh` against a disposable remote when testing delivery. Never use a production repository
for the first end-to-end run.

Run the same work request independently in VS Code, Copilot CLI, and Claude Code.

For `pr-review` and `pr-resolve`, open a disposable pull request against that remote, add a couple
of review comments and a plain conversation comment to it, and check out its head branch before
invoking either skill.

For `repo-pr-status`, seed the disposable remote with open pull requests matching the acceptance
matrix: a draft, one labeled `blocked`, one with a change request and no push since, one with a
failing required check, one with a merge conflict, one approved with green CI, one with no reviews,
one whose linked issue is closed, one with a "superseded by #N" comment, one approved with a
long-running pending check, one approved but blocked by a required status check that never
reports, one with an unanswered `COMMENTED` review, one with an unanswered conversation comment,
one partially approved under a two-approval rule, and one whose base is a deleted `feature/x`
branch. Also run once from a non-repository directory. Record
`gh pr list --state open --json number,updatedAt,labels,reviewDecision` before and after the run;
the output must be identical.

## Acceptance matrix

| Scenario | Expected result |
| --- | --- |
| New request | Creates `request.md` and valid `state.json` |
| Planning | Uses the native Planner, writes `plan.md`, and stops |
| No plan approval | Implementer refuses without edits |
| Revised plan | Writes a suffixed plan, changes `currentPlan`, clears approval, and stops |
| Explicit plan approval | Creates or uses a non-default branch and implements |
| First implementation edit | Runs a focused check immediately afterward |
| Configured validation | Runs explicitly configured or repository-required commands once |
| Implementation completion | Reports exact changed paths and does not stage or commit |
| Independent review | Reads the complete diff, reuses validation results, reports reviewed paths, and does not edit |
| Review findings | Stops for human direction without automatic repair |
| Clean review | Reports ready for delivery and stops for a later user request |
| No delivery request | Makes no commit, push, or pull-request side effects |
| Missing or unauthenticated `gh` | Delivery blocks before commit |
| Protected or secret path | Delivery blocks and stages nothing |
| Unrelated working-tree change | Preserved and excluded from staged paths |
| Explicit delivery request | Stages only reviewed paths, commits, pushes, and creates a draft PR |
| Delivery request asking for a ready-for-review PR | Creates a non-draft PR |
| Delivery with an existing PR for the branch | Pushes and does not edit the PR's title, body, or draft or ready state |
| Draft PR creation fails | Delivery blocks without retrying with or without `--draft`; the report says the commit and push already happened and gives the exact `gh pr create` command |
| Ready-for-review request with an existing draft PR | Pushes, does not run `gh pr ready`, reports the command as a skipped action, and ends `delivered` |
| Existing-PR check fails with a `gh` error | Delivery blocks before commit |
| New chat session | Resumes the named run from `state.json` and current artifacts |
| Multiple active runs | Lists candidates and asks instead of guessing |
| New research request | Creates `request.md` and valid `state.json` at stage `intake` |
| Researching | Uses the native Researcher, writes `findings.md`, and advances to `critiquing` |
| Critiquing | Uses the native Skeptic, writes `critique.md`, and advances to `synthesizing` |
| Synthesizing | Uses the native Merger, writes `recommendation.md`, and stops at `recommendation_review` |
| No human response at recommendation review | Makes no further stage transition |
| Requested revision | Repeats the needed stage, writes a suffixed artifact, and stops again at `recommendation_review` |
| Accepted recommendation | Sets stage `completed` and stops |
| No open PR for current branch | `pr-review`/`pr-resolve` stop with a blocker instead of guessing a PR |
| New `pr-review` request | Derives the work ID from the PR number and fetches existing comments |
| PR review findings | Excludes findings that substantively repeat an existing comment |
| No findings approval | Makes no `gh` posting call |
| PR head moved before posting | Posting blocks instead of anchoring to a stale diff position |
| Explicit findings approval | Posts one `COMMENT`-event review with correctly anchored inline comments |
| New `pr-resolve` request | Derives the work ID from the PR number and catalogs every comment |
| Comment catalog | Numbers every review-thread and issue comment and assigns each a recommendation |
| No plan approval | `pr-resolve` Implementer refuses without edits |
| Explicit plan approval | Implements only the "fix now" items from the approved plan |
| `pr-resolve` delivery | Commits each planned group separately, pushes once, and replies per comment |
| Comment needing no reply | Gets no reply (pure observation or compliment) |
| Comment resolved by a change | Gets a reply naming the commit that addressed it |
| Comment with no change made | Gets a reply with the plan's recorded reasoning |
| Re-run against the same PR | Never double-posts or double-replies |
| Context is not a single GitHub repository | `repo-pr-status` asks for the target `owner/name` instead of guessing |
| Unauthenticated `gh` for `repo-pr-status` | Stops at `collection_blocked` |
| `repo-pr-status` run | Writes `snapshot.json`, `config.json`, `rules.md`, and `report.md`, stops at `reported`, and makes no mutating `gh` call |
| Summary counts | Add up to the snapshot PR count, which equals `openPrTotal` unless truncated |
| Exactly `maxPullRequests` open PRs | Not truncated |
| More than `maxPullRequests` open PRs | Truncated, header shows true total |
| Draft PR | `draft` with bold `draft` |
| PR labeled `blocked` | `blocked` with bold `blocked-label` |
| Change requested, no push since | `waiting-on-author` with bold `changes-requested` |
| Same PR after a push | `needs-review` with bold `re-review`, plus `change-request-not-dismissed` |
| Failing required check | `waiting-on-author` with bold `ci-failing` |
| Merge conflict | `waiting-on-author` with bold `merge-conflict` |
| Approved, green CI | `ready-to-merge` with bold `approved` |
| No reviews | `needs-review` with bold `first-review`, plus `no-reviewers` |
| Linked issue closed | `possibly-obsolete` with bold `linked-issues-closed` |
| "superseded by #N" comment | `possibly-obsolete` with bold `superseded-mention` |
| Reclassify with `staleDays: 0` and `obsoleteDays: null` | Every PR without evidence tags is `stale` with bold `inactive`, written to `report-2.md` without fetching again |
| Reclassify with `obsoleteDays: 0` | `possibly-obsolete` with bold `abandoned` |
| PR both failing CI and stale | `stale` with bold `inactive` and plain `ci-failing` |
| Reclassify with the same config | Same statuses and tags as the previous report |
| Simulated per-PR fetch failure | That PR is `unclassified` with `data-gap` and listed under Data gaps |
| Approved, CI pending | `blocked` with bold `awaiting-ci`, plain `ci-pending` |
| Approved, CI passing, required check never reports | `blocked` with bold `blocked-by-protection` |
| Unanswered `COMMENTED` review | `waiting-on-author` with bold `awaiting-author-reply` |
| Unanswered conversation comment | `waiting-on-author` with bold `awaiting-author-reply` |
| Bot comment newer than the last push | Not `awaiting-author-reply`; the bot is not `lastActor` |
| Author replies after that comment | `needs-review` with bold `re-review` |
| Partial approval under `REVIEW_REQUIRED`, no requests | `needs-review` with bold `review-pending` |
| Deleted base `feature/x` | `possibly-obsolete` with bold `base-branch-missing` |
| Fetch failure on a PR labeled `stale` | `unclassified` with bold `data-gap`, plain `stale-label` |
| Run from a non-repository directory | Asks for `owner/name`, creates no run directory, and is not `collection_blocked` |
| `owner/name` supplied from outside a repository | Collects with `gh repo view <owner/name>`, `--repo`, and GraphQL variables, creates the run directory under the current directory, and reaches `reported` |
| Two fresh runs in the same second | Second run gets a `-2` suffixed work ID |
| Fork PR head branch matches another PR's base | Not `stacked-on-open-pr` |
| `owner/name` differs from local checkout | Override file not read; recorded in `request.md` |
| Every report row | Has at least one bold tag |

Inspect Git status, the staged diff, commit contents, remote branch, pull-request body, and run state
after each applicable scenario.

## Clean-install release test

Use a clean profile or isolated test environment:

1. Install from `mpalmerlee/startbuilding` in Copilot CLI and confirm VS Code Agent Host discovers
   that installation.
2. Confirm VS Code exposes one agent set with the expected delegated tool boundaries.
3. Add the public repository as a Claude marketplace and install `startbuilding@startbuilding`.
4. Repeat component discovery and one complete disposable-repository workflow.
5. Bump to a temporary test version and verify each client's update behavior before publishing the
   actual release version.
