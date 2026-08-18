# LUMI Development & Deployment Workflow

## Branch strategy

- `main` — production branch. Only merged, reviewed code lives here.
- `development` — integration branch. Active feature work and experiments merge here first.
- Feature branches — short-lived branches off `development` for a single change.

```
main (production, protected)
  ^
  |  PR + review + required checks
  |
development (integration)
  ^
  |  PR + review
  |
feature/...  fix/...  refactor/...
```

## What changed

1. `lumi-fastapi-react-v3.2` was renamed to `development`.
2. `.github/workflows/vercel-deploy.yml` no longer triggers on `push` to `main`. It is `workflow_dispatch` only, so production Vercel deploys require a manual run from the Actions tab.
3. `.github/workflows/deploy.yml` (DigitalOcean) is also `workflow_dispatch` only, with an `environment: production` gate.
4. `.github/workflows/vercel-preview.yml` deploys a Vercel preview on every push to `development` (or `develop`).
5. `.github/workflows/ci.yml` now runs on pushes and PRs to `main` and `development`.

## Manual GitHub settings you still need to configure

Pushing code to `main` should be blocked at the repository level. These settings cannot be committed to the repo; they must be set in the GitHub UI or via the `gh` CLI.

### 1. Branch protection for `main`

Go to **Settings → Branches → Add rule** and apply to `main`:

- **Require a pull request before merging** → required approving reviews: at least 1
- **Require status checks to pass before merging**:
  - `Backend Tests`
  - `Frontend Tests`
  - `Docker Build Check`
- **Restrict who can push to matching branches** → allow only administrators, or restrict pushes to `main` entirely
- **Do not allow bypassing the above settings**

### 2. GitHub environment for `production`

Go to **Settings → Environments → production**:

- Add the users or teams who can approve the `environment: production` jobs.
- Enable **Required reviewers**.

### 3. Vercel project settings

In the Vercel dashboard for this project:

- **Git → Production Branch** = `main`
- **Git → Ignored Build Step** (optional): add `npx vercel-ignore-build` if you want Vercel's native Git integration to ignore branches handled by GitHub Actions.
- Disable **Auto-Deploy on Push** for `main` if you want production deploys to be fully manual through the GitHub Action.

## How to deploy

### Promote `development` to production

1. Open a pull request from `development` to `main`.
2. Wait for all status checks to pass and get at least one approving review.
3. Merge the PR.
4. Go to **Actions → Vercel Production Deploy** (and/or **Deploy**) and run the workflow manually.

### Deploy a preview of `development`

Push to `development`. The `Vercel Preview Deploy` workflow runs automatically and posts a preview URL.

## Notes

- The production deploy workflows still require `github.ref == 'refs/heads/main'`, so they cannot be accidentally triggered from another branch.
- The `development` branch is now the default place for new work. Create feature branches from it, not from `main`.
