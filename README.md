# LFX Actions

[![License](https://img.shields.io/github/license/jmertic/lfx-tac-actions)](LICENSE)
[![CI](https://github.com/jmertic/lfx-tac-actions/workflows/CI/badge.svg)](https://github.com/jmertic/lfx-tac-actions/actions?query=workflow%3ACI+branch%3Amain)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=jmertic_lfx-tac-actions&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=jmertic_lfx-tac-actions)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=jmertic_lfx-tac-actions&metric=coverage)](https://sonarcloud.io/summary/new_code?id=jmertic_lfx-tac-actions)

LFX Actions are a series of tools that can be either ran directly at the CLI or leveraged via GitHub Actions, which automate pulling data from LFX for using with other tools and services. The current list of tools provided is as below:

- `updateprojects`: Pulls hosted project data from a project's landscape and streams in CSV format to `stdout`.
- `updatetacmembers`: Pulls the current list of TAC members from LFX PCC and streams CSV format to `stdout`.
- `updatetacagendaitems`: A tool for TACs that use a GitHub Project for managing their TAC agenda. Streams TAC agenda items in CSV format to `stdout`..
- `updateclomonitor`: Pulls hosted project data from a project's landscape in YAML format to `stdout` that can imported into [CLOMonitor](https://github.com/cncf/clomonitor).
- `updatecharters`: Downloads the Technical Charters for the subprojects of a project identified by `--slug`, saving them in the current working directory with naming format of `SLUG_charter`.
- `updatedecks`: Exports Google Slides and Powerpoint decks from Google Drive, saving them in PDF and PPTX format in the current working directory.
- `updateartwork`: Downloads the logo for the subprojects of a project identified by `--slug`, saving them in the current working directory with naming format of `SLUG/primary/color/SLUG-primary-color.svg` and updating the `SLUG/README.md` as appropriate.

You can run any of these commands with the `-h` flag to see the command line arguments required.

## Installation ( GitHub Action )

### Setup a token for the app to use

There are three options to pick from.

#### GitHub App (best option)

You can create a [GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app) for your organization, with the permissions as listed below.

- Organizations / Projects - Read-only
- Repository / Contents - Read & Write
- Repository / Pull requests - Read & Write
- Repository / Metadata - Read-only

[Generate a Private Key](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps#generating-private-keys) and go to your repository where the workflow runs, and under Settings > Secrets and Variables > Actions set:

- Variable `APP_CLIENT_ID`: Found on your App's "General" page under "Client ID".
- Secret `APP_PRIVATE_KEY`: Open the .pem file you downloaded and paste the entire content (including the `-----BEGIN RSA PRIVATE KEY-----` lines).

#### Personal Access Token (PAT)

Add a [repository secret](https://docs.github.com/en/actions/reference/encrypted-secrets) for `PAT`, which is a [GitHub Personal Authorization Token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) set for the `read:org`, `read:project`, and `repo` scope.

#### Use the `GITHUB_TOKEN` token

As a fallback, you can use the built in `GITHUB_TOKEN`. You have to review the permissions for the `GITHUB_TOKEN` for your repository ( more details [here](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication#permissions-for-the-github_token) ). Note that you need to ensure `GITHUB_TOKEN` has the permission to merge PRs (more [here](https://docs.github.com/en/organizations/managing-organization-settings/disabling-or-limiting-github-actions-for-your-organization#preventing-github-actions-from-creating-or-approving-pull-requests)).

> [!NOTE]
> `updatetacagendaitems` does not work with `GITHUB_TOKEN`; you must use a GitHub App or Personal Access Token (PAT).

### Workflows

#### `updatedatafromlfx.yml`

Add the one of the following blocks of code to a file `.github/workflows/updatedatafromlfx.yml`

##### GitHub App version

```yaml
name: Update Data From LFX
on:
  issues:
    types:
      - "labeled"
      - "unlabeled"
  schedule:
    - cron: '0 0 * * *' # set to when you would like this to run
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1 # v3.2.0
        id: app-token
        with:
          client-id: ${{ vars.APP_CLIENT_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
      - uses: jmertic/lfx-tac-actions@3cc53bcc460908d9a414290e83e8104357b0d652 # 20260908
        with:
          # refer to https://github.com/jmertic/lfx-tac-actions/blob/main/action.yml#L3 for the various inputs to set. 
        env:
          token: ${{ steps.app-token.outputs.token }}
          repository: ${{ github.repository }}
          ref: ${{ github.ref }}
```

##### Personal Access Token (PAT) or `GITHUB_TOKEN` token version

If you are using a Personal Access Token (PAT), substitute `secrets.GITHUB_TOKEN` below with the secret name you are using ( i.e `secrets.PAT` ).

```yaml
name: Update Data From LFX
on:
  issues:
    types:
      - "labeled"
      - "unlabeled"
  schedule:
    - cron: '0 0 * * *' # set to when you would like this to run
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: jmertic/lfx-tac-actions@3cc53bcc460908d9a414290e83e8104357b0d652 # 20260908
        with:
          # refer to https://github.com/jmertic/lfx-tac-actions/blob/main/action.yml#L3 for the various inputs to set. 
        env:
          token: ${{ secrets.GITHUB_TOKEN }}
          repository: ${{ github.repository }}
          ref: ${{ github.ref }}
```

#### Dependabot setup

(OPTIONAL BUT HIGHLY RECOMMENDED) Setup dependabot for keeping GitHub Actions updated automatically. Two files to add:

##### `dependabot.yml`.

Add the following to a file `.github/dependabot.yml`.

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    groups:
      all:
        dependency-type: "production"
```

##### `dependabot-automerge.yml` 

Add the one of the following blocks of code to a file `.github/workflows/dependabot-automerge.yml`

###### GitHub App version

```yaml
name: Auto-merge Dependabot PRs

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: write
  pull-requests: write

jobs:
  dependabot:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'

    steps:
      - uses: actions/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1 # v3.2.0
        id: app-token
        with:
          client-id: ${{ vars.APP_CLIENT_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
      - name: Checkout
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
        with:
          token: ${{ steps.app-token.outputs.token }}
          ref: ${{ github.head_ref }}
          persist-credentials: false
      - name: Approve PR
        run: |
          gh pr review --approve "${{ github.event.pull_request.number }}"
        env:
          GH_TOKEN: ${{ steps.app-token.outputs.token }}
      - name: Enable auto-merge
        run: |
          gh pr merge \
            --squash \
            --auto \
            "${{ github.event.pull_request.number }}"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

##### Personal Access Token (PAT) or `GITHUB_TOKEN` token version

If you are using a Personal Access Token (PAT), substitute `secrets.GITHUB_TOKEN` below with the secret name you are using ( i.e `secrets.PAT` ).

```yaml
name: Auto-merge Dependabot PRs

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: write
  pull-requests: write

jobs:
  dependabot:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'

    steps:
      - name: Checkout
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
      - name: Approve PR
        run: |
          gh pr review --approve "${{ github.event.pull_request.number }}"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Enable auto-merge
        run: |
          gh pr merge \
            --squash \
            --auto \
            "${{ github.event.pull_request.number }}"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Auto-merging changes into the repository
 
If the build results in data that differs from the current data in the given repository, a pull request is created to apply those changes. This pull request is by default set to be [automatically merged](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request) only if the following conditions are met.

- The target repository must have **[Allow auto-merge](https://docs.github.com/en/github/administering-a-repository/managing-auto-merge-for-pull-requests-in-your-repository)** enabled in settings.
- The pull request base must have a branch protection rule with at least one requirement enabled.
- The pull request must be in a state where requirements have not yet been satisfied. If the pull request is in a state where it can already be merged, the action will merge it immediately without enabling auto-merge.

### Installation (Local)

You can install this tool on your local computer via [`pipx`](https://pipx.pypa.io).

```bash
pipx install git+https://github.com/jmertic/lfx-tac-actions.git
```

Similarly, you can use the command below to upgrade your local install.

```bash
pipx upgrade lfx-tac-actions
```

All of the commands referenced above will be available for executing directly.
