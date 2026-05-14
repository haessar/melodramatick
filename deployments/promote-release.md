# Promoting a Release to Production

This guide documents the current Melodramatick release flow: tag a release
from `master`, then merge that exact tag into `production`.

The examples below use `v0.2.0`. Change the tag consistently when promoting a
later release.

## Create the release tag from master

Start from `master` and make sure it is up to date.

```bash
git checkout master
git pull origin master
```

Run the test suite against the validation app.

```bash
DJANGO_SETTINGS_MODULE=testtick.settings DATABASE_URL=sqlite:////tmp/melodramatick-test.sqlite3 python manage.py test
```

Check that the release commit is clean and tagged correctly.

```bash
git status
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin master v0.2.0
```

*Alternatively, create the tag directly in the "New release" interface on GitHub.*

Create the GitHub Release from the pushed tag.

## Merge the release into production

Switch to `production` and update it.

```bash
git checkout production
git pull origin production
```

Merge the release tag without committing immediately.

```bash
git merge --no-commit --no-ff v0.2.0
```

Inspect the staged merge before committing.

```bash
git status
git diff --cached --name-status
```

Restore any production-only files that should not be removed by the `master` merge, e.g.:

```bash
git restore --source=HEAD -- deployments/hetzner.md
```

*Or by unstaging files for deletion in the vscode GUI.*

Inspect the final staged merge.

```bash
git status
git diff --cached --name-status
```

Commit the promotion.

```bash
git commit -m "Promote v0.2.0 to production"
```

## Submodules

Production uses deployment-specific submodules. Make sure they are present and
at the intended commits.

```bash
git submodule update --init --recursive
git status
```

If a submodule needs to be advanced, update it explicitly inside that submodule
and commit the changed submodule pointer on `production`.

## Deploy

Pushing the promotion commit to `production` triggers the GitHub Actions
deployment workflow in `.github/workflows/deploy.yml`.

After committing the promotion, push `production`:

```bash
git push origin production
```

Check the GitHub Actions run after pushing. For the current host inventory,
deployment commands, service names, and troubleshooting commands, see
`deployments/hetzner.md`.
