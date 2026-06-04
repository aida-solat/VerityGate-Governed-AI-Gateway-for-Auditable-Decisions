# Releasing VerityGate

> Built & designed by **Deciwa**.

This project uses [Semantic Versioning](https://semver.org). Release notes live
in `docs/RELEASE_NOTES_v<version>.md` and the running history in
[`CHANGELOG.md`](../CHANGELOG.md).

## Checklist

1. Ensure `main` is green (CI passes: backend pytest + frontend lint/build).
2. Bump the version:
   - `backend/app/__init__.py` → `__version__`
   - `frontend/package.json` → `version`
3. Move `CHANGELOG.md` items from **Unreleased** into a dated version section.
4. Write `docs/RELEASE_NOTES_v<version>.md`.
5. Commit: `chore(release): v<version>`.

## Tag and push

```bash
# Tag the release (annotated)
git tag -a v0.1.0 -m "VerityGate v0.1.0"
git push origin v0.1.0
```

## Create the GitHub release

Using the GitHub CLI, with the prepared notes as the body:

```bash
gh release create v0.1.0 \
  --title "VerityGate v0.1.0" \
  --notes-file docs/RELEASE_NOTES_v0.1.0.md
```

Or via the web UI: **Releases → Draft a new release → choose tag `v0.1.0` →**
paste the contents of `docs/RELEASE_NOTES_v0.1.0.md`.

## After release

- Add a new **Unreleased** section to `CHANGELOG.md`.
- Verify the release badge and links in the README resolve.

---

Built & designed by **Deciwa**.
