Work on a GitHub issue from the public `dsmrreader/dsmr-reader` repository. Takes an issue number as input.

## 1. Fetch the issue
No `gh` CLI is available here — use the public GitHub REST API directly. It's unauthenticated (fine for
low, occasional request volume; public repos need no token for reads):
```bash
curl -s https://api.github.com/repos/dsmrreader/dsmr-reader/issues/<number>
curl -s https://api.github.com/repos/dsmrreader/dsmr-reader/issues/<number>/comments
```

## 2. Understand the request
Read the title, body, and comments. Identify whether it's a bug report, feature request, or question,
and what's actually being asked. Search the codebase for the relevant area before changing anything.

Then interview the prompter before implementing — ask about anything the issue leaves ambiguous:
scope, expected behavior, edge cases, which of several plausible interpretations to follow. Do this
even in auto mode; a GitHub issue is written for the maintainer's own judgment, not as a full spec, so
don't guess at intent on their behalf. Only skip asking if the issue is fully unambiguous.

## 3. Implement
Don't start writing code until the user has given an explicit, unambiguous go-ahead to implement —
not a vague "continue" or "yes" that could just as easily mean "keep discussing/proposing." If there's
any doubt what a reply confirms, ask directly rather than inferring permission to start coding.

Follow the project's existing conventions (service layer, DTOs, type hints, signals, etc. — see
`.claude/rules/dsmrreader/general.md`). Keep the change scoped to what the issue asks for.

## 4. Validate
Run `/dsmrreader:quality-check`. Stop and report if any step fails — do not commit until it's clean.

## 5. Commit
Reference the issue number in the commit message, e.g. `fix: ... (#<number>)`.
