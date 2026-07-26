# StartBuilding

StartBuilding is a human-in-the-loop software delivery plugin for VS Code, GitHub Copilot CLI, and
Claude Code. Give it a work request and focused agents plan the change, implement it, review it, and
prepare a pull request without spending implementation tokens before plan approval or performing
Git delivery before you ask.

StartBuilding uses the coding-agent host, Git, and local Markdown and JSON artifacts. It does not
run a background service, database, scheduler, or separate orchestration UI.

## How it works

StartBuilding coordinates five focused roles:

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
  final delivery stage. Planning, implementation, and review do not require `gh`.

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

StartBuilding deliberately keeps orchestration local and visible. The repository remains the source
of truth for architecture and validation, Git remains the source of truth for changes, and the
developer remains the authority over plan approval and delivery.
