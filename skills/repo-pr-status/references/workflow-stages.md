# Workflow stages

Use only these stages:

```text
intake -> collecting -> classifying -> reported | collection_blocked
reported -> classifying (explicit reclassify request; writes the next suffixed report)
```

Update `state.json` only after the corresponding artifact has been written successfully. There is
no human approval gate: nothing in this workflow changes anything on GitHub.

## Start or resume

1. Read `AGENTS.md`, applicable repository instructions, and the run selection rules in the
   artifact contract.
2. Run `gh auth status`. Stop at `collection_blocked` if `gh` is missing or unauthenticated.
3. Select the target repository:
   - If the user named `owner/name`, run
     `gh repo view <owner/name> --json nameWithOwner,defaultBranchRef`.
   - Otherwise, run `git rev-parse --show-toplevel` and then
     `gh repo view --json nameWithOwner,defaultBranchRef` from the current directory.
   - If either command fails because the context is not a single Git repository with a GitHub
     remote (no repository, a multi-root workspace, or no GitHub remote), ask the user for the
     target `owner/name` and stop until they answer. Never guess. This is not
     `collection_blocked`, and no run directory is created before the user answers. Once the user
     supplies `owner/name` from such a non-repository context, the artifact root is the current
     working directory and the run directory is created under it.
   - Only a failed lookup of an explicitly named repository (not found or no access) stops at
     `collection_blocked`.

   After resolution, every `gh pr` call passes `--repo <nameWithOwner>`, and every `gh api graphql`
   call passes `-f owner=<owner> -f name=<name>`. `gh auth status` takes no repository argument.
4. For a new request, derive the work ID `repo-pr-status-<YYYYMMDD>-<HHMMSS>` from the current UTC
   time. If that run directory already exists under the artifact root, append the next free
   numeric suffix (`-2`, `-3`, and so on). Create the run directory, `request.md`, and initial
   `state.json` with stage `intake`. Record the resolved `nameWithOwner` and default branch in
   `request.md`.
5. For a resumed request, validate the state shape and current artifact pointers before choosing a
   transition.

## Intake

Record the target repository, any threshold overrides, and the request text in `request.md`.
Resolve `config.json` from, lowest to highest precedence: the bundled
`skills/repo-pr-status/assets/repo-pr-status-config.json`, the target repository's
`.startbuilding/repo-pr-status.json` when present, and overrides stated in the request. Read the
repository override file only when the artifact root is a Git checkout whose
`gh repo view --json nameWithOwner` matches the target repository; otherwise record "repository
override file not read: target is not the local checkout" in `request.md`. Overrides stated in the
request always apply. No REST call is made to fetch the override file. Copy
`skills/repo-pr-status/references/status-rules.md` exactly to `rules.md`. Set stage `collecting`.

## Collecting

Every GitHub call is read-only. Never run `gh pr comment`, `gh pr review`, `gh pr merge`,
`gh pr close`, `gh pr edit`, `gh pr ready`, `gh pr reopen`, any `gh issue` write, or any `gh label`
command. `gh api` switches to POST when `-f` or `-F` fields are passed, so any REST call must use an
explicit `-X GET`; this workflow makes no REST calls. `gh api graphql` sends only `query`
operations, never a `mutation`; passing `-f`/`-F` to it is the normal way to send a read-only
`query` and its variables.

1. The repository and default branch were already resolved at start; reuse them.
2. Count open pull requests with one read-only GraphQL `query`, before the list call:
   `gh api graphql -f owner=<owner> -f name=<name> -f query='query($owner:String!,$name:String!){repository(owner:$owner,name:$name){pullRequests(states:OPEN){totalCount}}}'`.
   Record the result as `openPrTotal`. Then list open pull requests:
   `gh pr list --repo <nameWithOwner> --state open --limit <maxPullRequests> --json number,title,url,author,isDraft,createdAt,updatedAt,baseRefName,headRefName,isCrossRepository,labels,reviewDecision,reviewRequests,additions,deletions,changedFiles`.
   Set `truncated` when `openPrTotal` exceeds the number of listed pull requests.
3. For each pull request:
   `gh pr view <number> --repo <nameWithOwner> --json commits,statusCheckRollup,mergeable,mergeStateStatus,headRepository,body`
4. For each pull request, one `gh api graphql` `query`:

   ```sh
   gh api graphql -f owner=<owner> -f name=<name> -F number=<n> -f query='query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){pullRequest(number:$number){baseRef{name} closingIssuesReferences(first:20){totalCount nodes{number state}} comments(last:20){totalCount nodes{author{login __typename} createdAt body}} reviews(last:20){totalCount nodes{author{login __typename} state submittedAt body}} latestReviews(first:100){nodes{author{login __typename} state submittedAt}} reviewThreads(first:100){totalCount nodes{isResolved comments(last:20){totalCount nodes{author{login __typename} createdAt}}}}}}}'
   ```

   A null `baseRef` means the base branch is missing. Comments, reviews, and review threads come
   only from this query, because `author.__typename` (`Bot` or `User`) is the only reliable bot
   signal; `gh pr view` returns a bare login with no type. Use `-f` for `owner` and `name` so they
   stay strings, and `-F` for `number`.

Trim the data as the artifact contract describes and write `snapshot.json` with `snapshotAt` set to
the UTC time collection started.

If a call for one pull request fails, record the pull request number and error in `errors[]` and
continue; the Analyst marks it `unclassified`. Stop at `collection_blocked` only when `gh auth
status`, the explicit repository lookup, the open pull request count query, or the list call
fails. Set stage `classifying`.

## Classifying

Invoke the native Analyst with the run directory. It reads only `snapshot.json`, `config.json`, and
`rules.md`, and uses `snapshotAt` as "now". Persist the exact result to the next report artifact,
set `currentReport`, set stage `reported`, and stop. Tell the user the report path and the summary
counts.

## Reclassify

A later explicit request may change thresholds or labels for an existing run. Update `config.json`,
record the change in `request.md`, set stage `classifying`, and invoke the Analyst again against the
same snapshot. The result is written to the next suffixed report, such as `report-2.md`. Fresh data
always means a new run; never re-collect into an existing snapshot.
