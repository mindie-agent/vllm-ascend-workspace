# Workspace guidance

These instructions apply to using this workspace for vLLM and vLLM Ascend development. Before modifying the workspace's own scripts, configuration, shared agent resources, or documentation, read [CONTRIBUTING.md](CONTRIBUTING.md).

- Before changing code in a submodule or task worktree, read that repository's `AGENTS.md` at its checked-out revision, if present, and any more specific `AGENTS.md` applicable to the target files. Consult its contribution instructions when preparing commits or PRs.
- `vllm/` and `vllm-ascend/` are separate source repositories referenced by submodules. For source development, create or reuse their worktrees at the task's selected revisions inside a task directory under `.worktrees/`; see [.worktrees/README.md](.worktrees/README.md). Worktrees of the same source repository share branches and remotes, while each has its own checkout.
- When updating branches in `vllm-ascend` to resolve conflicts with the target branch, use `git rebase` onto the updated target branch rather than `git merge`. Resolve conflicts during the rebase and continue with `git rebase --continue`. For `vllm`, just use `git merge`.
- Before initializing source repositories, creating worktrees, initializing tasks, or cleaning directories, read [.agents/scripts/README.md](.agents/scripts/README.md) for the corresponding helper, configuration, and path rules.
- During normal workspace installation or GitHub authentication repair, follow [.agents/github-authentication.md](.agents/github-authentication.md) before source/fork initialization. Reuse working authentication; otherwise guide browser login or enterprise-network token creation/input. Reuse an enclosing MindIE Agent setup's verified login.
- After the user agrees to create or reuse this workspace, follow [.agents/harness-workspace.md](.agents/harness-workspace.md) to add its root to the current harness's native workspace/project facility in the same setup flow. Reuse existing registration and report its actual status separately from source initialization.
- Read the selected skill's `SKILL.md`. For configuring discovery from different working directories, consult [.agents/README.md](.agents/README.md).
- Use native local tools for local work. Prefer available MindIE Agent tools for remote NPU operations. Observe remote jobs through the backend that created them; inspect the original receipt before retrying an uncertain operation.
- Limit cleanup to the objects or scope authorized by the user. Query PR status when it is needed to assess cleanup eligibility.
- Keep task progress and experiment records in the task's record and result locations, separate from reusable instructions; see [.worktrees/README.md](.worktrees/README.md).

## Formatting checks

- Run `pre-commit run --from-ref <base> --to-ref <head> --hook-stage manual` in the target worktree, using the current PR or requested commit range.

## Remote script paths and executor identity

- Before remote script execution, read the executor's name or employee ID from `user_id` in untracked `.vaws-local/user.json`; ask and save it if missing. Use it as a directory component in the actual host and container script `cwd` paths, and place container scripts in a user-specific directory such as `/workspace/scripts/<user_id>/`.
- Keep weights and other large files on host data volumes, never the root filesystem. Verify backing mounts, including container mappings, and free space before writing.
