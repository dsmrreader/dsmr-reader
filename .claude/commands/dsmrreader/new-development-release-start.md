---
description: "Open the next development cycle right after a production release: bump VERSION to beta 1, stub the changelog, update dependencies."
disable-model-invocation: true
---

Start a new development cycle right after a production release. Only applies to the `development` branch.

Commit messages: single line, no body, no co-author trailer (see `.claude/rules/dsmrreader/general.md`).

## 1. Switch to development
If not already on the `development` branch, check it out first, and make sure the working tree is clean:
```bash
git -C /app checkout development
git -C /app status --short
```

## 2. Bump the version to beta 1
In `src/dsmrreader/__init__.py`, bump the `VERSION` tuple to beta 1 of the next version: stage `"beta"`, number `1`.
- Default is the next **minor** (minor `+1`, patch resets to `0`). Example: `(6, 2, 0, "final", 0)` → `(6, 3, 0, "beta", 1)`.
- If a changelog section for the next **patch** release already exists, or the user says a patch release is planned, use that patch version instead.
  Example: `(6, 2, 3, "final", 0)` → `(6, 2, 4, "beta", 1)`. Ask when it is unclear which one is meant.

## 3. Stub the changelog
In `documentation/docs/reference/changelog.md`, add (or relabel) the heading for the new version directly below the intro divider,
above the previous release's entry:
```markdown
## v6.3.0 - Unreleased
```
Leave a new section empty — entries get added as features/fixes land during the cycle.

## 4. Commit
Commit the version bump and changelog stub together, e.g. `release: start v6.3.0 beta 1`.

## 5. Update dependencies
Run `/dsmrreader:dependency-update`.

## 6. Validate
Run `/dsmrreader:quality-check` (includes the development image build). Stop and report if any step fails — do not commit until it's clean.

## 7. Commit dependency updates
Once validation passes, commit the dependency update changes, e.g. `chore: package and web library updates`.
