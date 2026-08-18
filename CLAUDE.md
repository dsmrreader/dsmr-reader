## Git Workflow

The git repository root is mounted at `/app`. Always use `-C /app` for all git commands, regardless of the current working directory (`/app/src`).

Always run `git -C /app status` before committing to verify exactly which files will be included.

Stage and commit using the repo root:
```bash
git -C /app add <file-relative-to-/app>
git -C /app commit -m "..."
```

File paths shown in `git -C /app status` are relative to `/app` (e.g. `src/.claude/settings.local.json`).
