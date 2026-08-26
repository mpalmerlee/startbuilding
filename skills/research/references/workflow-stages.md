# Workflow stages

Use only these stages:

```text
intake
  -> researching
  -> critiquing
  -> synthesizing
  -> recommendation_review
  -> revising | completed
```

Update `state.json` only after the corresponding artifact has been written successfully.

## Start or resume

1. Read `AGENTS.md`, applicable repository instructions, optional `.startbuilding/project.json`,
   and the run selection rules in the artifact contract.
2. For a new request, create the run directory, `request.md`, and initial `state.json` with stage
   `intake`.
3. For a resumed request, validate the state shape and current artifact pointers before choosing a
   transition.
4. Preserve unrelated working-tree changes. Report them before continuing the run.

## Intake

Record the research question, scope, and any constraints in `request.md`. Set stage `researching`.

## Researching

Invoke the native Researcher with the request, run path, repository instructions, and prior
findings when revising. The Researcher must not edit or execute.

Persist its exact result to the next findings artifact, set `currentFindings`, and set stage
`critiquing`.

## Critiquing

Invoke the native Skeptic with the request and `currentFindings`. The Skeptic must not edit or
execute.

Persist its exact result to the next critique artifact, set `currentCritique`, and set stage
`synthesizing`.

## Synthesizing

Invoke the native Merger with the request, `currentFindings`, and `currentCritique`. The Merger must
not edit or execute.

Persist its exact result to the next recommendation artifact, set `currentRecommendation`, set stage
`recommendation_review`, and stop. Tell the user the artifact path and ask for approval or
revisions.

## Recommendation review

Continue only after an explicit human response to the current recommendation.

- If the human requests revisions, determine which stage needs to repeat. Invoke the Researcher,
  Skeptic, or Merger again as needed, persist suffixed artifacts, update the matching current
  pointer, set stage `researching` (or the specific repeated stage), and stop again at
  `recommendation_review` once synthesis completes.
- If the human accepts the recommendation, set stage `completed` and stop.

Never infer acceptance from silence or from approval recorded in another run.
