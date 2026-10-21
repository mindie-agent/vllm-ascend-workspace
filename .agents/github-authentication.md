# GitHub sign-in before workspace setup

[Chinese](github-authentication.zh.md)

Run this step during normal workspace installation or GitHub authentication
repair, before initializing source repositories and fork remotes. It works
without an installed MindIE Agent plugin. Reuse answers and authentication
already verified in the enclosing MindIE Agent installation.

1. Install `gh` if needed, then run
   `gh api --hostname github.com user --jq .login` with a bounded wait.
   If the expected account works, reuse it without asking for another login.
   A username by itself is not proof of authentication.
2. If login is needed, offer browser or token login. Prefer a token when the
   user reports an enterprise network, proxy/custom CA settings are present,
   or browser authorization is blocked. Resolve network, proxy 407 and
   certificate failures as transport problems; keep TLS verification enabled.
3. For browser login, run
   `gh auth login --hostname github.com --git-protocol https --web`.
   For token login, ask only whether the user has a token or needs to create
   one. Open the [token creation page](https://github.com/settings/tokens/new?scopes=repo%2Cread%3Aorg%2Cgist&description=MindIE%20Agent)
   when needed. The standard persistent flow uses the classic PAT scopes
   requested by `gh`; honor organization expiry, SSO and token-type policy.
4. Receive an existing token in a user-operable terminal:
   `gh auth login --hostname github.com --git-protocol https`, then select
   `Paste an authentication token` and use the hidden prompt. If the user
   supplied a private file, feed it through stdin to
   `gh auth login --hostname github.com --git-protocol https --with-token`.
   Let `gh` save the credentials. Keep token contents out of chat, arguments,
   logs, `workspace.json`, `.vaws-local` and repository remotes.
   A stale `GH_TOKEN` or `GITHUB_TOKEN` overrides saved login; repair that
   caller's credential source before retrying login. For fine-grained PATs,
   follow the environment-only reuse flow linked below.
5. Verify the expected account, ensure `git`'s directory is on `PATH`, and on Windows
   clear any unscoped `helper-selector` in system `etc/gitconfig` (`git config --system --unset-all credential.helper`
   and `GCM_INTERACTIVE=never`; if Windows `schannel` behind a corporate proxy reports
   `CRYPT_E_NO_REVOCATION_CHECK`, set `http.sslBackend=schannel` and `http.schannelCheckRevoke=false`
   with `http.sslVerify=true`), then run `gh auth setup-git --hostname github.com`, and read
   the actual source/fork repositories needed by initialization. Reuse saved fork selections; a
   different authenticated account does not authorize replacing them.
   `repo_init.py` configures existing forks; it does not create GitHub forks.
   Resolve missing forks within the user's requested setup before claiming
   the workspace is ready for pushes.

For saved login, verify an account lookup in a new process without
`GH_TOKEN`/`GITHUB_TOKEN` under the same user and `GH_CONFIG_DIR`. Existing
environment-only credentials are also valid, but must reach the processes
performing later operations; foreground success does not prove independent
background authentication. Detailed token, permission and service handling
follows the shared [MindIE Agent sign-in flow](https://github.com/mindie-agent/mindie-agent/blob/main/docs/enterprise-network.en.md#github-sign-in-flow).
Only after authentication is ready, continue the existing workspace
initialization instructions; do not ask for the same login again.
