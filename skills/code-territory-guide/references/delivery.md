# Authorized Git Delivery

Load this reference before creating a commit, pushing, opening a pull request,
tagging, releasing, merging, or performing another delivery operation. Read
`safety-and-scope.md` first.

## Delivery Authorization

Treat delivery as a separate capability after implementation, validation, and owned-diff review. Authorization for editing does not imply authorization to commit; authorization to commit does not imply authorization to push, open a pull request, tag, or release.

Perform a delivery operation only when it is:

- explicitly requested in the current task
- covered by a clear standing user instruction
- required by a repository workflow the user explicitly invoked

Interpret common requests narrowly:

- **Implement or fix**: edit and validate, then leave the owned delta uncommitted.
- **Commit this**: create one local commit containing only the authorized task-owned delta.
- **Commit and push**: create the local commit and push the authorized branch.
- **Open a pull request**: push if necessary and open the requested pull request, but do not merge it.
- **Release or tag**: perform only the specifically requested release operation after verifying the intended commit.

## Before Committing

1. Recheck the branch, concise status, and staged state.
2. Confirm the requested completion state and relevant validation.
3. Review the exact task-owned diff and the staged diff.
4. Stage explicit owned paths or hunks. Avoid broad staging commands when unrelated changes exist.
5. Preserve pre-existing staged files and user-owned changes. Do not unstage, rewrite, or include them without authorization.
6. Check for secrets, generated artifacts, local configuration, raw evaluation evidence, and other unintended content.
7. Resolve the repository's commit-message convention using the rules below.
8. Create a message that describes the verified behavior or repository outcome.
9. Allow normal commit hooks to validate the message.
10. Verify the resulting commit and report its hash plus anything intentionally left uncommitted.

## Commit-message Conventions

Resolve the format independently for every repository. Use this precedence:

1. An explicit message or convention in the current user request.
2. Trusted repository instructions such as scoped `AGENTS.md`, `CONTRIBUTING.md`, or delivery documentation.
3. Repository configuration such as a commit template, Commitlint configuration, Conventional Commits rules, or issue/PR workflow documentation.
4. A small recent sample of relevant commits, preferably affecting the same area.
5. A concise imperative summary as the fallback.

Prefer documented configuration over inconsistent history. Inspect only enough history to establish the pattern; do not broaden discovery after the convention is supported.

Use ticket, Jira, issue, component, or team prefixes only when established by trusted context such as:

- the explicit request
- the current branch name
- an assigned issue or pull request
- trusted repository workflow metadata

Never invent or guess an identifier. If the repository requires one and none can be established, ask for it before committing. If a prefix is optional or history is inconsistent, use the safest documented format or the fallback rather than blocking.

Follow normal commit hooks. Do not use `--no-verify`, suppress message validation, or weaken repository rules unless explicitly authorized. If a hook rejects the message, preserve the work, report the exact failure, and make only a convention-compliant correction. Do not amend or rewrite an existing commit unless that history operation is separately authorized.

Fallback message:

```text
<Imperative description of the verified outcome>
```

Add a body only when it materially explains motivation, compatibility, migration, validation, or a non-obvious tradeoff.

Do not create a normal completion commit while required task-caused validation is failing. Create an incomplete or work-in-progress commit only when the user explicitly requests that checkpoint and label it honestly.

## Before Pushing or Publishing

Before pushing, verify the remote, destination branch, upstream relationship, and commits to be sent. Never force-push, rewrite published history, merge, tag, release, or delete a branch unless that specific operation is authorized.

Do not run destructive commands or bulk data-changing operations unless explicitly requested and allowed by platform constraints.
