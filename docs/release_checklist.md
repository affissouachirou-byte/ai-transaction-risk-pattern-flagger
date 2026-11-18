# Public GitHub release checklist

## Deliverable checks
- [ ] Copy this package's source/notebook/scripts/docs/tests into the local project without copying its `data/validated/` or `data/outputs/` datasets.
- [ ] Confirm dry-run of at least one known customer-month and structural evaluation (already observed on reference setup).
- [ ] Run `python -m pytest tests -q` using your `.venv` and record test results.
- [ ] Verify README source names, model name, current requirements and runbook correspond to the actual committed code.
- [ ] Check four-case manual caveats in `docs/evaluation_report.md`.

## Privacy and security (must be done before making repo public)
- [ ] No live identifiers, third-party confidential data, private datasets, employment records, or credentials anywhere in the intended repository.
- [ ] `git status --short` and `git ls-files` review before commit.
- [ ] Inspect `git ls-files data` to confirm `data/validated/` and `data/outputs/` are absent.
- [ ] Run a local secret scan against tracked files; check Git history and earlier commits for exposed secrets (a clean current working tree does not clean Git history).
- [ ] Never publish actual local investigation files unless manually reviewed/sanitized and approved; filenames with synthetic IDs are not proof of safe content.
- [ ] Check `.gitignore` including `.env`, `.venv`, `*.log`, and outputs.
- [ ] Verify no bulky files committed inadvertently, and repo starts private until reviewed.
- [ ] Publish with clear 'synthetic only' and 'not production ready' labels.

## Release decision
- [ ] All evidence verified from the user's local project; no claim of comprehensive model validation.
- [ ] Commit and tag only after user reviews GitHub visibility and release notes.
