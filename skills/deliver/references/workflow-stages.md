# Workflow stages

Use only these stages:

```text
planning
  -> plan_review
  -> implementation
  -> implementation_blocked | automated_review
  -> changes_requested | review_approval
  -> delivered | delivery_blocked
```

Update `state.json` only after the corresponding artifact has been written successfully.

## Start or resume

1. Read `AGENTS.md`, applicable repository instructions, optional `.startbuilding/project.json`,
   and the run selection rules in the artifact contract.
2. For a new request, create the run directory, `request.md`, and initial `state.json` with stage
   `planning`.
3. For a resumed request, validate the state shape and current artifact pointers before choosing a
  transition.
4. Preserve unrelated working-tree changes. Report them before implementation and delivery.

## Planning

Invoke the native Planner with the request, run path, repository instructions, controlling code
surface, nearby tests, and discovered validation commands. The Planner must not edit or execute.

Persist the exact result to the next plan artifact, set `currentPlan`, clear `planApproval`, set
stage `plan_review`, and stop. Tell the user the artifact path and ask for approval or revisions.
Never implement in the turn that creates or revises a plan.

## Plan approval and branch preparation

Continue only after explicit user approval of `currentPlan`. Record that approval as defined by the
artifact contract and require `planApproval.artifact` to equal `currentPlan` before implementation.

Determine the default branch from the remote HEAD or repository metadata. Before editing, require a
non-default branch. Create `<branchPrefix><work-id>` when needed without resetting, cleaning,
stashing, or discarding existing changes. Set stage `implementation` only after these checks pass.

If the user requests plan changes, invoke the Planner again, persist a suffixed plan, clear prior
approval, and stop at `plan_review`.

## Implementation

Invoke the native Implementer with the approved plan, run path, existing-change summary, and
validation policy. After its first substantive edit, the Implementer runs the narrowest relevant
check. It then runs only commands explicitly configured in `.startbuilding/project.json` or
required by applicable repository instructions.

Persist its exact report to the next implementation artifact and set `currentImplementation`.
Copy only its explicit repository-relative changed-path list into `implementationPaths` after
checking those paths against the actual diff. Do not include unrelated changes.

If the report ends `Status: blocked`, set stage `implementation_blocked` and stop. Otherwise set
stage `automated_review`.

## Independent review

Invoke the native Reviewer with all current artifacts, repository instructions, the complete
working-tree diff, and `implementationPaths`. The Reviewer may execute focused checks but must not
edit.

Persist its exact report to the next review artifact, set `currentReview`, copy its explicit reviewed
path list into `reviewedPaths`.

- For `Verdict: changes requested`, set stage `changes_requested`, report findings, and stop for
  human direction. Do not automatically repair findings.
- For `Verdict: ready for delivery`, require `reviewedPaths` to cover every `implementationPaths`
  entry, set stage `review_approval`, present the review, and stop for delivery confirmation.
- Any missing or malformed verdict blocks the workflow.

When the user directs repairs, determine whether the approved plan still covers them. If scope or
behavior changes, revise the plan and obtain fresh plan approval. Otherwise record the direction,
clear stale review state, invoke the Implementer for a suffixed implementation artifact, and review
again.

## Delivery confirmation

Continue only when the user explicitly requests delivery after the current review. Treat that
request as an action, not a stored approval record, and invoke the Committer.

The Committer must block unless all of these are true:

- the current plan matches the recorded plan approval;
- the review verdict is `ready for delivery`;
- `reviewedPaths` covers all and only intended `implementationPaths`;
- the current branch is not the default branch;
- no reviewed path matches protected paths or likely secret files;
- `git status` and the complete diff have been inspected;
- `gh` is installed and authenticated before any commit is created.

Stage each reviewed implementation path explicitly. Never use `git add .`, `git add -A`, or commit
all current changes. Inspect the staged diff and require it to contain only reviewed paths. Do not
bypass Git hooks.

Create a focused commit, push the current branch, and create or update a pull request with `gh`.
Build the pull-request body from the current plan, implementation, review, and validation results.
Persist the exact Committer report as `delivery.md` and set stage `delivered`. On any failure, avoid
further side effects, persist the report, set stage `delivery_blocked`, and explain what remains.
