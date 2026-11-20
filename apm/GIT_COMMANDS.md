# IncidentLens — Git commands (backup → test branch → main)

Run in Kiro's terminal (PowerShell) at the repo root, **one line at a time**.
PowerShell tip: use `;` to chain commands, not `&&`.

---

## 1. Back up the current work to its own branch

```powershell
git checkout main
git pull
git checkout -b backup-t01-t04
git add -A
git commit -m "Backup: T01-T04 work before v0.9.0"
git push -u origin backup-t01-t04
```

If `git commit` says *nothing to commit*, that's fine: the branch still captures the current state.

---

## 2. Create a test branch from main

```powershell
git checkout main
git checkout -b test-v0.9.0
```

---

## 3. Replace the files (BUILD_PLAN R01) and verify (R02)

1. File Explorer → View → show **hidden items**.
2. In the repo, delete everything **except** `.git`, `.kiro\specs`, `.kiro\hooks`.
3. Extract `incidentlens-v0.9.0.zip` elsewhere → open its `incidentlens` folder → select all → copy into the repo root.
4. Add the private docs (git-ignored, never pushed):
   - `HANDOVER.md` → repo root
   - `BUILD_PLAN.md` → repo root
   - `apm-notes.md` → `docs\apm-notes.md`

Check nothing private will be committed:

```powershell
git status --short
```

`HANDOVER.md`, `BUILD_PLAN.md`, `docs/apm-notes.md` and `examples/scenarios/` must **not** be listed.

Then in a new Kiro chat (Haiku 5.5): `Do R02 from #BUILD_PLAN.md` → expect **75 passed**.

---

## 4. Commit and push the test branch

```powershell
git add -A
git commit -m "IncidentLens v0.9.0: full package, scenarios, evaluation, tests"
git push -u origin test-v0.9.0
```

Review the branch in GitLab before it touches main.

---

## 5. Merge into main, tag, push

```powershell
git checkout main
git pull
git merge --no-ff test-v0.9.0 -m "Merge test-v0.9.0 into main"
git tag v0.9.0
git push origin main --tags
```

**If `main` is protected** and the push is rejected: open a merge request `test-v0.9.0 → main` in GitLab, merge it there, then:

```powershell
git checkout main
git pull
git tag v0.9.0
git push origin v0.9.0
```

---

## 6. Verify

```powershell
git log --oneline -3
git ls-files | Select-String "HANDOVER|BUILD_PLAN|apm-notes"
```

The second command must print **nothing**.

---

## Undo (only if the merge went wrong)

Restores main to the backup. `--force` overwrites main on GitLab: use with care.

```powershell
git checkout main
git reset --hard backup-t01-t04
git push --force origin main
```

---

## Later: final release (BUILD_PLAN R15)

```powershell
# after setting version: 1.0.0 in apm.yml and deleting .apm\skills\hello-incidentlens (if present)
git checkout -b release-v1.0.0
git add -A
git commit -m "IncidentLens v1.0.0"
git push -u origin release-v1.0.0
git checkout main
git pull
git merge --no-ff release-v1.0.0 -m "Release v1.0.0"
git tag v1.0.0
git push origin main --tags
```

Never move or delete an existing tag; fixes go out as `v1.0.1`.
