# Workflow stages

Use only these stages:

```text
intake -> cataloging -> plan_review -> implementation
       -> implementation_blocked | delivery
       -> delivered | delivery_blocked
```

Update `state.json` only after the corresponding artifact has been written successfully.

## Start or resume

1. Read `AGENTS.md`, applicable repository instructions, optional `.startbuilding/project.json`,
   and the run selection rules in the artifact contract.
2. Run `gh auth status`. Stop with a concrete blocker if `gh` is missing or unauthenticated.
3. Run `gh pr view --json number,url,state,headRefName,baseRefName,title,body,isDraft` for the
   current branch. Stop if there is no open pull request for this branch; never search for or
   guess a different PR.
4. Derive the work ID from the pull request number, such as `pr-42-resolve`.
5. For a new request, create the run directory, `request.md`, and initial `state.json` with stage
   `intake`.
6. For a resumed request, validate the state shape and current artifact pointers before choosing a
   transition.
7. Preserve unrelated working-tree changes. Report them before implementation and delivery.

## Intake

Record the pull request identity, URL, base and head branch names, and head SHA in `request.md`.
Fetch the pull request diff (`gh pr diff` or `git diff <base>...<head>`) and every existing comment
on the pull request, including review-thread comments (resolved or not) and plain conversation
comments, and persist both as plain files (`diff.patch` and `existing-comments.md`) in the run
directory. The Planner has no shell access and reads only what is persisted here. Set stage
`cataloging`.

## Cataloging

Invoke the native Planner with the persisted diff, the persisted existing-comment snapshot,
repository instructions, and nearby tests. The Planner has no tool access beyond reading files: it
cannot edit, execute, or fetch anything itself.

The Planner assigns a stable number to each comment or review thread, records its kind
(`review-thread` or `issue-comment`), root comment ID or URL, file and line when it applies, author,
and quoted text; assigns a category and a recommendation (fix now, reply-only with no change, or no
action needed, each with a one-line reason) to each numbered item; and produces one implementation
plan covering only the items recommended "fix now", mapping every planned change back to the
comment numbers it addresses and grouping changes the way they should later be committed.

Persist the exact result to the next plan artifact, set `currentPlan`, clear `planApproval`, set
stage `plan_review`, and stop. Tell the user the artifact path and ask for approval or revisions.
Never implement in the turn that creates or revises the plan.

## Plan approval and branch check

Continue only after explicit user approval of `currentPlan`. Record that approval as defined by the
artifact contract and require `planApproval.artifact` to equal `currentPlan` before implementation.

Confirm the current branch is still the pull request's head branch and is not the repository's
default branch. Set stage `implementation` only after these checks pass.

If the user requests plan changes, invoke the Planner again, persist a suffixed plan, clear prior
approval, and stop at `plan_review`.

## Implementation

Invoke the native Implementer with the approved plan, run path, existing-change summary, and
validation policy. After its first substantive edit, the Implementer runs the narrowest relevant
check, then only commands explicitly configured in `.startbuilding/project.json` or required by
applicable repository instructions.

Persist its exact report to the next implementation artifact and set `currentImplementation`. The
Implementer never commits, pushes, or replies to pull request comments.

If the report ends `Status: blocked`, set stage `implementation_blocked` and stop. Otherwise set
stage `delivery`.

## Delivery

Invoke the native Committer with the approved plan, the implementation report, and the full comment
catalog. The Committer stages and commits each planned group separately, pushes once after all
commits land, and replies to each catalogued comment: no reply for "no action needed" items, a reply
naming the commit that addressed a "fix now" item, or a reply carrying the plan's recorded reasoning
for a "reply-only, no change" decision. Review-thread comments get a threaded reply; plain
conversation comments get a new comment that references the original.

Persist the exact result to `delivery.md`, record which comment numbers were replied to, and set
stage `delivered` or `delivery_blocked`.
