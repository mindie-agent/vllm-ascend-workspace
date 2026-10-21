# Open the workspace in the current harness

[中文](harness-workspace.zh.md) | English

Run this step after the user agrees to create or reuse this workspace and the
directory exists, including standalone installation. That choice includes adding
the selected path to the current harness; do not ask for another confirmation.
Reuse a registration for the same absolute path. Initialization can finish later.

Use the current harness's native project tools or directory picker first. If it
exposes an authenticated native API, use its installed schema. Register the
workspace root, not the plugin checkout, a source submodule, or a temporary task
worktree. Keep existing projects and contribution scope intact.

| Harness | Native action |
| --- | --- |
| Codex desktop | Use the native **Add project** folder picker or an available project-management tool. `codex app "<absolute-path>"` can open a workspace on macOS; check `codex app --help` and the installed platform. On Windows the CLI may only print the path, so complete **Add project** in the app. Confirm the project list contains the selected path. |
| Codex CLI | Start the next interactive session with `codex -C "<absolute-path>"`. This selects the session root; it does not register a desktop project. |
| Claude Code desktop | Use the native local folder selector. If the installed CLI supports `--desktop`, launch `claude --desktop` with the workspace as the process working directory, then confirm the selected folder in the app. |
| Claude Code CLI | Launch `claude` with the workspace as the process working directory. `--add-dir` adds access to another directory; it does not change the project's root. |
| Kimi Code Web | Use its native working-directory/session picker. When the installed Web API exposes `POST /api/sessions/`, create an empty session with `{"work_dir":"<absolute-path>","create_dir":false}` through that same authenticated server; reuse an existing session for the path. Check the returned `work_dir` and the native directory list (`GET /api/work-dirs/` where supported). Do not send a model prompt just to register a directory. |
| Kimi Code CLI | Use `kimi --work-dir "<absolute-path>"` when supported by the installed `kimi --help`, or launch `kimi` from that directory. |
| DeepSeek Harness | Use the native workspace picker or the active client's `workspace/create` operation. DSH `0.2.0-rc.2` exposes `ctx.remote.workspace.create({path: "<absolute-path>"})`; it returns the existing record for an already registered path. Check the successful native response and workspace list. Use the running host's directory, profile and authenticated client. |
| Cursor / other editors | Use the native **Open Folder** or **Add Folder to Workspace** action for the selected path, and confirm it in the editor. |

Use available UI automation to finish native folder selection. If that UI is not
accessible to the agent, give the exact path and the remaining native folder
selection action. Report the directory as prepared and registration as pending;
do not claim that a shell `cd` registered it. Do not modify private project
databases, manufacture a new client profile, or start nested model runs.

After registration, report the absolute path, native registration/open status and
source initialization status together. A download failure leaves the registered
directory available for resuming initialization.

Native interface references: [Codex CLI](https://developers.openai.com/codex/cli/reference/),
[Claude Code CLI](https://code.claude.com/docs/en/cli-reference),
[Kimi sessions](https://github.com/MoonshotAI/kimi-cli/blob/main/src/kimi_cli/web/api/sessions.py),
[DSH workspace controller](https://www.npmjs.com/package/@deepseek-ai/dsh-api-workspace-controller/v/0.2.0-rc.2).
