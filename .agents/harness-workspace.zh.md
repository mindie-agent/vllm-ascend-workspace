# 在当前客户端打开工作区

中文 | [English](harness-workspace.md)

用户同意创建或复用本工作区、目录已经存在后，立即执行此步骤；独立安装也包含这一步。该选择包含把所选路径添加到当前客户端，不再单独询问是否登记。相同绝对路径已有记录时直接复用，源码初始化可以稍后完成。

优先使用当前客户端的原生项目工具或目录选择器；使用原生认证 API 时按已安装版本的接口执行。登记工作区根目录，保留已有项目和知识贡献范围。

| 客户端 | 原生操作 |
| --- | --- |
| Codex 桌面版 | 使用原生 **Add project / 添加项目** 目录选择器或可用的项目管理工具。macOS 可以用 `codex app "<绝对路径>"` 打开工作区，先核对本机 `codex app --help` 与平台能力。Windows CLI 可能只打印路径，需要继续在应用内添加项目，并确认项目列表中的路径。 |
| Codex CLI | 下一次交互会话使用 `codex -C "<绝对路径>"`，设置会话根目录；这一步不等于登记桌面项目。 |
| Claude Code 桌面版 | 使用原生本地目录选择器。本机支持 `--desktop` 时，以工作区为进程工作目录启动 `claude --desktop`，再确认应用中的所选目录。 |
| Claude Code CLI | 以工作区为进程工作目录启动 `claude`。`--add-dir` 只增加目录访问范围，不改变项目根目录。 |
| Kimi Code Web | 使用原生工作目录/会话选择器。已安装 Web API 支持 `POST /api/sessions/` 时，在同一个已认证服务上用 `{"work_dir":"<绝对路径>","create_dir":false}` 创建空会话；同一路径已有会话时直接复用。核对响应的 `work_dir` 和原生目录列表（支持时使用 `GET /api/work-dirs/`），无需发起模型请求。 |
| Kimi Code CLI | 本机 `kimi --help` 支持时使用 `kimi --work-dir "<绝对路径>"`，或从该目录启动 `kimi`。 |
| DeepSeek Harness | 使用原生工作区选择器或当前客户端的 `workspace/create` 操作。DSH `0.2.0-rc.2` 提供 `ctx.remote.workspace.create({path: "<绝对路径>"})`，同一路径已登记时返回已有记录。核对成功响应与工作区列表，使用正在运行的宿主目录、profile 和已认证客户端。 |
| Cursor / 其他编辑器 | 用原生 **Open Folder / 打开文件夹** 或 **Add Folder to Workspace / 将文件夹添加到工作区**，并在编辑器内确认路径。 |

有 UI 自动化能力时直接完成目录选择。Agent 无法操作该 UI 时，给出确切路径和剩余的原生目录选择动作，报告“目录已准备、登记待完成”。不把子 shell 的 `cd` 当成登记成功，不修改宿主私有项目数据库，不创建另一份客户端 profile，不为登记路径启动嵌套模型任务。

最后一起报告绝对路径、宿主登记/打开状态和源码初始化状态。下载失败时保留已登记的目录，后续直接恢复初始化。

原生接口依据：[Codex CLI](https://developers.openai.com/codex/cli/reference/)、[Claude Code CLI](https://code.claude.com/docs/en/cli-reference)、[Kimi 会话](https://github.com/MoonshotAI/kimi-cli/blob/main/src/kimi_cli/web/api/sessions.py)、[DSH workspace controller](https://www.npmjs.com/package/@deepseek-ai/dsh-api-workspace-controller/v/0.2.0-rc.2)。
