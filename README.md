# LFX Actions

[![License](https://img.shields.io/github/license/jmertic/lfx-tac-actions)](LICENSE)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=jmertic_lfx-tac-actions&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=jmertic_lfx-tac-actions)

LFX Actions are a series of tools that can be either ran directly at the CLI or leveraged via GitHub Actions, which automate pulling data from LFX for using with other tools and services. The current list of tools provided is as below:

- `updateprojects` pulls hosted project data from a project's landscape into a CSV file.
- `updatetacmembers` pull the current list of TAC members from LFX PCC into a CSV file.
- `updatetacagendaitems` is for TACs that use a GitHub Project for managing their TAC agenda; the tool exports the data into a CSV file.
- `updateclomonitor` pulls hosted project data from a project's landscape into a file that can imported into [CLOMonitor](https://github.com/cncf/clomonitor)
- `updatecharters` pulls the Technical Charters for the subprojects of a project, saving them in a specified directory with naming format of `SLUG_charter`
- `updatedecks` exports Google Slides and Powerpoint decks from Google Drive, saving them in PDF and PPTX format in a specified directory.

You can run any of these commands with the `-h` flag to see the command line arguments required.

## Installation

### GitHub Action

Add the following to a file `.github/workflows/updatedatafromlfx.yml`

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
      - uses: jmertic/lfx-tac-actions@main
        with:
          # refer to https://github.com/jmertic/lfx-tac-actions/blob/main/action.yml#L3 for the various inputs to set. 
        env:
          token: ${{ secrets.PAT }} # Must be set as a secret for the repo; required access is 'read:discussion, read:org, read:project, repo'
          repository: ${{ github.repository }}
          ref: ${{ github.ref }}
```

#### Auto-merging changes into the repository
 
If the build results in data that differs from the current data in the given repository, a pull request is created to apply those changes. This pull request is by default set to be [automatically merged](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request) only if the following conditions are met.

- The target repository must have **[Allow auto-merge](https://docs.github.com/en/github/administering-a-repository/managing-auto-merge-for-pull-requests-in-your-repository)** enabled in settings.
- The pull request base must have a branch protection rule with at least one requirement enabled.
- The pull request must be in a state where requirements have not yet been satisfied. If the pull request is in a state where it can already be merged, the action will merge it immediately without enabling auto-merge.

### Local install

You can install this tool on your local computer via [`pipx`](https://pipx.pypa.io).

```bash
pipx install git+https://github.com/jmertic/lfx-tac-actions.git
```

Similarly, you can use the command below to upgrade your local install.

```bash
pipx upgrade lfx-tac-actions
```

All of the commands referenced above will be available for executing directly.
