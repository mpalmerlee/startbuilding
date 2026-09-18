# Workflow stages

Use only these stages:

```text
intake -> reviewing -> findings_review -> posting -> posted | posting_blocked
                                        -> reviewing (revise findings)
```

Update `state.json` only after the corresponding artifact has been written successfully.

## Start or resume

1. Read `AGENTS.md`, applicable repository instructions, and the run selection rules in the
   artifact contract.
2. Run `gh auth status`. Stop with a concrete blocker if `gh` is missing or unauthenticated.
3. Run `gh pr view --json number,url,state,headRefName,baseRefName,title,body,isDraft` for the
   current branch. Stop if there is no open pull request for this branch; never search for or
   guess a different PR.
4. Derive the work ID from the pull request number, such as `pr-42-review`.
5. For a new request, create the run directory, `request.md`, and initial `state.json` with stage
   `intake`.
6. For a resumed request, validate the state shape and current artifact pointers before choosing a
   transition.
7. Preserve unrelated working-tree changes. Report them before continuing the run.

## Intake

Record the pull request identity, URL, base and head branch names, and head SHA in `request.md`.
Fetch the pull request diff (`gh pr diff` or `git diff <base>...<head>`) and every existing comment
on the pull request, including review-thread comments (resolved or not) and plain conversation
comments, and persist both as plain files (`diff.patch` and `existing-comments.md`) in the run
directory. The Reviewer has no shell access and reads only what is persisted here. Set stage
`reviewing`.

## Reviewing

Invoke the native Reviewer with the persisted diff, the pull request description, repository
instructions, and the persisted existing-comment snapshot. The Reviewer has no tool access beyond
reading files: it cannot edit, execute, or fetch anything itself. It must read every existing
comment before drafting findings and drop any finding that substantively repeats one.

Persist the exact result to the next findings artifact, set `currentFindings`, set stage
`findings_review`, and stop. Tell the user the artifact path and ask which findings to post.

## Findings review

Continue only after an explicit human response identifying which findings to post, with any edits.

- If the human requests revised findings, invoke the Reviewer again, persist a suffixed findings
  artifact, update `currentFindings`, and stop again at `findings_review`.
- If the human approves a set of findings, record exactly that set, including edits, as the
  approved posting scope, and set stage `posting`.

Never infer approval from silence or from approval recorded in another run.

## Posting

Re-fetch the pull request head SHA and compare it to the one recorded at intake. If it has moved,
stop and require the findings to be reviewed again before posting, since inline diff positions are
anchored to a specific commit.

Invoke the native Commenter with only the approved posting scope and the current head SHA. The
Commenter posts one pull-request review with `event: COMMENT`, anchoring each finding that names a
concrete file and line as an inline comment, and folding any other approved finding into the
review's top-level body. It must never use `APPROVE` or `REQUEST_CHANGES`, and never merge, close,
or edit the pull request's title, description, or labels.

Persist the exact result to `posted.md`, record the posted comment IDs and URLs in `state.json`,
and set stage `posted` or `posting_blocked`.
