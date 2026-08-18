Start a new development cycle right after a production release. Only applies to the `development` branch.

## 1. Switch to development
If not already on the `development` branch, check it out first:
```bash
git -C /app checkout development
```

## 2. Bump to next minor, beta 1
In `src/dsmrreader/__init__.py`, bump the `VERSION` tuple to the next minor version, beta 1: major stays the same, minor `+1`, patch resets to `0`, stage `"beta"`, number `1`.
Example: `(6, 2, 0, "final", 0)` → `(6, 3, 0, "beta", 1)`.

## 3. Stub the changelog
In `documentation/docs/reference/changelog.md`, add a new empty heading for the new version directly below the intro divider, above the previous release's entry:
```markdown
## v6.3.0 - Unreleased
```
Leave it empty — entries get added as features/fixes land during the cycle.

## 4. Commit
Commit the version bump and changelog stub together on `development`.

## 5. Update dependencies
Run `/dsmrreader:dependency-update`.

## 6. Validate
Run `/dsmrreader:quality-check`. Stop and report if any step fails — do not commit until it's clean.

## 7. Commit dependency updates
Once validation passes, commit the dependency update changes on `development`.

That concludes the directive.
