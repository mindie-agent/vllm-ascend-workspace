# 工作区初始化前的 GitHub 登录

[English](github-authentication.md)

正常安装工作区或修复 GitHub 认证时，在初始化源码仓库和 Fork 远端之前执行这一步，无需先安装 MindIE Agent 插件。从 MindIE Agent 安装流程进入时，复用已经核实的登录和用户选择。

1. 缺少 `gh` 时先安装，然后有界执行 `gh api --hostname github.com user --jq .login`。当前账号可用且符合预期，就直接复用，不再次询问登录方式。只有用户名不代表已经认证。
2. 需要登录时提供浏览器和 Token 两种方式。用户说明处于企业网络、检测到代理/自定义 CA 或浏览器授权受阻时，优先 Token。网络超时、代理 407 和证书错误先按传输问题处理，保留 TLS 校验。
3. 浏览器方式执行 `gh auth login --hostname github.com --git-protocol https --web`。Token 方式只询问“已有 Token 还是需要创建”；需要时打开 [Token 创建页](https://github.com/settings/tokens/new?scopes=repo%2Cread%3Aorg%2Cgist&description=MindIE%20Agent)。普通持久登录使用 `gh` 要求的 classic PAT 权限，尊重组织对有效期、SSO 和 Token 类型的要求。
4. 已有 Token 时，在用户可操作的终端执行 `gh auth login --hostname github.com --git-protocol https`，选择 `Paste an authentication token` 后在隐藏提示中输入。用户已提供私有文件时，直接通过标准输入交给 `gh auth login --hostname github.com --git-protocol https --with-token`。由 `gh` 保存凭据；Token 不进入对话、命令行参数、日志、`workspace.json`、`.vaws-local` 或仓库远端 URL。
5. 再次核对账号，执行 `gh auth setup-git --hostname github.com`，并只读检查初始化需要的源码仓库和 Fork。保留已保存的 Fork 选择，登录账号变化不自动改写个人远端。`repo_init.py` 配置已有 Fork，不负责在 GitHub 创建 Fork；缺失时按用户请求的初始化范围处理，再报告推送就绪。

失效的 `GH_TOKEN` / `GITHUB_TOKEN` 会覆盖已保存的登录，先修正调用方的凭据来源，再重试登录。Fine-grained PAT 按下方共享流程使用环境变量认证。

持久登录需在相同用户和 `GH_CONFIG_DIR` 下、不带 `GH_TOKEN` / `GITHUB_TOKEN` 的新进程中验证。已有环境变量认证也可直接使用，但后续执行进程须能取得同一凭据；当前终端成功不等于独立后台进程已经认证。Token、权限与服务的详细处理沿用 [MindIE Agent 登录流程](https://github.com/mindie-agent/mindie-agent/blob/main/docs/enterprise-network.md#github-登录引导)。认证就绪后继续工作区原有初始化步骤，不重复要求用户登录。
