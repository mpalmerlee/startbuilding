# StartBuilding

StartBuilding is a plugin framework for human-in-the-loop agentic graphs of specialist agents in
VS Code, GitHub Copilot CLI, and Claude Code. Each graph is a resumable, file-backed workflow with
named roles, least-privilege tools, and explicit human gates. StartBuilding currently ships four
skill graphs:

- `deliver`: plans a change, implements it, reviews it, and prepares a pull request without
  spending implementation tokens before plan approval or performing Git delivery before you ask.
- `research`: investigates a technical question, gathers and critiques evidence, and synthesizes a
  recommendation for your review.
- `pr-review`: reviews the diff of the pull request for your current branch, skips anything
  already flagged on that PR, and posts only the comments you approve.
- `pr-resolve`: catalogs and numbers every comment on the pull request for your current branch,
  plans the fixes, implements them once you approve the plan, and replies to each comment once
  it's addressed.

StartBuilding uses the coding-agent host, Git, and local Markdown and JSON artifacts. It does not
run a background service, database, scheduler, or separate orchestration UI.

## How it works

StartBuilding coordinates the `deliver` graph's five focused roles:

- The **Coordinator** owns workflow state and delegates each stage.
- The **Planner** researches the repository and writes a concrete implementation plan. It cannot
  edit files or run commands.
- The **Implementer** applies an explicitly approved plan and runs focused validation. It cannot
  commit or push.
- The **Reviewer** independently checks the approved plan, implementation report, and complete
  working-tree diff. It cannot edit files.
- The **Committer** stages reviewed paths, commits, pushes, and creates or updates the pull request
  after an explicit delivery request. It cannot edit source code.

The delivery workflow is:

1. **Request**: StartBuilding records the work request in a local run directory.
2. **Plan**: the Planner researches the repository and produces a reviewable plan.
3. **Plan approval**: StartBuilding stops. Implementation begins only after you explicitly approve
   the current plan.
4. **Implementation**: the Implementer creates or uses a non-default branch, makes the approved
   changes, adds tests where appropriate, and validates the result.
5. **Independent review**: the Reviewer inspects the full diff and reports correctness defects,
   regressions, security risks, and missing tests.
6. **Delivery confirmation**: StartBuilding stops again and presents the review. A commit, push, or
  pull request requires a later explicit delivery request.
7. **Delivery**: the Committer verifies the staged diff, creates a focused commit, pushes the branch,
   and creates or updates the pull request with `gh`.

If a plan changes, its approval is invalidated. If review finds changes are needed, the workflow
stops for human direction instead of silently expanding the approved scope.

## How research works

StartBuilding also coordinates a separate, read-only research graph with four roles:

- The **Research Coordinator** owns workflow state and delegates each stage. It is the only role
  that writes `.startbuilding/runs/` artifacts for a research run.
- The **Researcher** gathers evidence and documents findings, from the repository and from external
  documentation on the web. It cites every source. It cannot edit files or run commands.
- The **Skeptic** adversarially critiques the findings, challenging assumptions and surfacing risks
  and evidence gaps. It can fetch the cited external sources to verify them rather than trusting
  them. It cannot edit files or run commands.
- The **Merger** synthesizes the findings and critique into a structured recommendation. It cannot
  edit files or run commands.

The research workflow is:

```text
intake -> researching -> critiquing -> synthesizing -> recommendation_review -> researching | completed
```

Each run is stored locally under:

```text
.startbuilding/runs/<work-id>/
|-- request.md
|-- findings.md
|-- critique.md
|-- recommendation.md
`-- state.json
```

StartBuilding stops at `recommendation_review` and presents the recommendation. Continuing to
`completed` or back to `researching` requires a later explicit human response.

## How PR review works

StartBuilding also coordinates a separate `pr-review` graph with three roles, scoped to the pull
request matching your currently checked-out branch:

- The **PR Review Coordinator** owns workflow state and delegates each stage.
- The **Reviewer** reads the pull request's diff and its existing comments, and reports findings
  the way a principal engineer would, dropping anything that substantively repeats a comment
  already on the PR. It cannot edit files or post anything.
- The **Commenter** posts only the findings you explicitly approve, as a single pull-request review
  with `event: COMMENT`. It cannot approve or request changes on the PR, merge it, close it, or
  edit its title, description, or labels.

The PR review workflow is:

```text
intake -> reviewing -> findings_review -> posting -> posted | posting_blocked
                                        -> reviewing (revise findings)
```

StartBuilding stops at `findings_review` and asks which findings to post. Before posting, it
re-checks the pull request's head commit against the one the findings were produced against, and
blocks instead of posting against a diff that has since moved.

Each run is stored locally under a work ID derived from the pull request number:

```text
.startbuilding/runs/pr-<number>-review/
|-- request.md
|-- findings.md
|-- posted.md
`-- state.json
```

## How PR resolve works

StartBuilding also coordinates a `pr-resolve` graph with four roles, scoped the same way as
`pr-review` but aimed at addressing feedback instead of producing it:

- The **PR Resolve Coordinator** owns workflow state and delegates each stage.
- The **Planner** catalogs every comment on the pull request, numbers it, assigns a category and a
  recommendation (fix now, reply-only, or no action), and writes an implementation plan for the
  "fix now" items, grouped the way they should later be committed. It cannot edit files or run
  commands.
- The **Implementer** applies an explicitly approved plan and runs focused validation. It cannot
  commit, push, or reply to comments.
- The **Committer** stages and commits each planned group separately, pushes once, and replies to
  each catalogued comment: no reply for a pure observation or compliment, a reply naming the commit
  that addressed a fix, or a reply with the plan's reasoning when no change was needed.

The PR resolve workflow is:

```text
intake -> cataloging -> plan_review -> implementation
       -> implementation_blocked | delivery
       -> delivered | delivery_blocked
```

StartBuilding stops at `plan_review` and asks you to approve the catalog and plan. There is no
independent-review stage here: implementation goes directly to delivery once you approve.

Each run is stored locally under a work ID derived from the pull request number:

```text
.startbuilding/runs/pr-<number>-resolve/
|-- request.md
|-- plan.md
|-- implementation.md
|-- delivery.md
`-- state.json
```

## Durable workflow state

Each run is stored locally under:

```text
.startbuilding/runs/<work-id>/
|-- request.md
|-- plan.md
|-- implementation.md
|-- review.md
|-- delivery.md
`-- state.json
```

These artifacts make the workflow reviewable and resumable across chat sessions. Plan approval
records the current plan artifact. A revision creates a new artifact and requires fresh approval;
delivery confirmation is not stored as a formal approval. Run artifacts are transient by default
and should be excluded from source control:

```gitignore
.startbuilding/runs/
```

StartBuilding follows the target repository's instructions. An optional
`.startbuilding/project.json` can define validation commands, protected paths, and the branch
prefix, but no initialization step is required.

## Requirements

- Git and a Git repository for the target project.
- One supported host: VS Code with GitHub Copilot, GitHub Copilot CLI, or Claude Code.
- GitHub CLI (`gh`) authenticated with permission to push and create pull requests when using the
  final `deliver` delivery stage. Planning, implementation, and review do not require `gh`.
- For `pr-review` and `pr-resolve`, `gh` authenticated with permission to read and comment on pull
  requests is required from the start, since both skills begin by resolving the pull request for
  your current branch.

## Install

### VS Code

Agent plugins are currently a Preview feature in VS Code. Enable `chat.plugins.enabled` and the
Agent Host, select the Copilot harness, then install StartBuilding through Copilot CLI:

```sh
copilot plugin install mpalmerlee/startbuilding
```

Reload VS Code and confirm that StartBuilding appears under **Agent Plugins - Installed**. VS Code
automatically discovers plugins installed under Copilot CLI's plugin directory.

You can enable, disable, update, or uninstall the plugin from the Agent Plugins view.

### GitHub Copilot CLI

Install directly from GitHub:

```sh
copilot plugin install mpalmerlee/startbuilding
```

Manage the installation with:

```sh
copilot plugin list
copilot plugin update startbuilding
copilot plugin disable startbuilding
copilot plugin enable startbuilding
copilot plugin uninstall startbuilding
```

VS Code also discovers plugins installed by Copilot CLI.

### Claude Code

Add the repository's plugin catalog, then install StartBuilding:

```sh
claude plugin marketplace add mpalmerlee/startbuilding
claude plugin install startbuilding@startbuilding
```

Manage the installation with:

```sh
claude plugin list
claude plugin update startbuilding@startbuilding
claude plugin disable startbuilding@startbuilding
claude plugin enable startbuilding@startbuilding
claude plugin uninstall startbuilding@startbuilding
```

## Use

Open a supported coding-agent chat in the repository you want to change and invoke the delivery
skill with a focused work request:

```text
/startbuilding:deliver Add rate limiting to the public login endpoint and cover it with tests
```

StartBuilding creates the run artifacts, delegates planning, and stops with the plan ready for your
review. Continue in the same conversation with explicit approval or requested revisions.

To resume in a later session, name the run directory and the action you want taken:

```text
/startbuilding:deliver Resume .startbuilding/runs/login-rate-limit and approve the current plan
```

When more than one unfinished run exists, StartBuilding asks you to select one rather than guessing.

Invoke the research skill with a focused investigation request:

```text
/startbuilding:research Investigate whether we should replace polling with webhooks for order status updates
```

StartBuilding creates the run artifacts, delegates evidence gathering, critique, and synthesis, and
stops with the recommendation ready for your review.

Check out the branch for an already open pull request, then invoke the PR review skill:

```text
/startbuilding:pr-review
```

StartBuilding resolves the pull request for your branch, delegates the diff review, and stops with
findings ready for your approval before posting anything.

Check out the branch for an already open pull request, then invoke the PR resolve skill to address
its feedback:

```text
/startbuilding:pr-resolve
```

StartBuilding catalogs every comment on the pull request, delegates planning, and stops with the
catalog and plan ready for your review before implementing anything.

## Safety boundaries

- Plan approval is never inferred from silence, an agent message, or approval from another run.
- A favorable automated review does not trigger delivery without an explicit user request.
- Planning and review are read-only roles enforced through host-native tool restrictions.
- Implementation never commits or pushes.
- Delivery never edits source files and stages only reviewed implementation paths.
- StartBuilding refuses to implement when plan approval names a different current plan or to deliver
  from the default branch.
- `.startbuilding/runs/`, environment files, credentials, protected paths, and unrelated changes are
  excluded from delivery.
- Existing user changes are preserved and reported when they prevent safe continuation.
- `pr-review` and `pr-resolve` require an open pull request for the current branch and never guess
  a different one.
- `pr-review` findings approval and `pr-resolve` plan approval are never inferred from silence, and
  neither skill posts, comments, or replies before that explicit approval.
- Neither skill can approve or request changes on a pull request, merge it, close it, or edit its
  title, description, or labels - only plain comments and replies are ever posted.
- `pr-review` re-checks the pull request's head commit immediately before posting and blocks
  instead of posting against a diff that has since moved.
- Both skills track which comments they have already posted or replied to, so a resumed run never
  double-posts.

StartBuilding deliberately keeps orchestration local and visible. The repository remains the source
of truth for architecture and validation, Git remains the source of truth for changes, and the
developer remains the authority over plan approval and delivery.
