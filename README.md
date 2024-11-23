# GitHub Action to sync data from LFX to a TAC repository

[![License](https://img.shields.io/github/license/jmertic/lfx-landscape-tools)](LICENSE)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=jmertic_lfx-tac-actions&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=jmertic_lfx-tac-actions)

## Installation

Add the following to a file `.github/workflows/updatedatafromlfx.yml`

```yaml
name: Update Data From LFX
on:
  issues:
    types:
      - "labeled"
      - "unlabeled"
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: jmertic/lfx-tac-actions@main
        with:
            landscape_url: # URL for the project's landscape; if blank, project data from the landscape won't be pulled
            artwork_url: # URL for the project's artwork repo; if blank, artwork from the artwork repo won't be pulled 
            lfx_tac_commmittee_url: # URL for the project's TAC committee in LFX; if blank, committee data won't be pulled
            tac_agenda_gh_project_url: # URL for the project's TAC agenda 
        env:
          token: ${{ secrets.PAT }} # Must be set as a secret for the repo; required access is 'read:discussion, read:org, read:project, repo'
          repository: ${{ github.repository }}
          ref: ${{ github.ref }}
```
