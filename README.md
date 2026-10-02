# Public GitHub Trending snapshots

This repository collects the public daily, weekly and monthly GitHub Trending pages for a learning discovery feed. It contains only the collector, tests, workflow and public project metadata. It is not an official GitHub API or a real-time, comprehensive popularity ranking.

## Updates and manual runs

The workflow runs at minute 17 every four hours UTC and can be run from Actions → Collect GitHub Trending → Run workflow. GitHub scheduled workflows can be delayed; inactive public repositories may have their schedules disabled after 60 days. Check the latest run and snapshot timestamps rather than assuming a scheduled run completed.

The output is `data/trending.json`. Each period records the source URL, last attempt, last successful fetch, status, repository names, descriptions, positions and available star counts. Failed collection retains the prior successful items and timestamp, writes a failed status, and makes the workflow fail visibly after saving that status. Missing statistics remain null.

## Permissions and safety

The collector uses Python's standard library and requests only three public github.com pages, with no API key, cookies or server credentials. It does not execute repository content. The workflow's temporary GITHUB_TOKEN has contents write permission only for this repository, to save snapshots. It has no deployment access. Third-party actions are pinned to a reviewed commit. Pull requests do not execute the collection workflow.

Consumers should validate the schema, repository names, timestamps and source URLs, retain local last-known-good data on failures, and mark snapshots older than 12 hours stale. Read the JSON through GitHub Contents API, not an untrusted download URL.

Standard GitHub-hosted runners for public repositories are free under the current GitHub billing rules; this workflow uses the standard ubuntu-24.04 runner and no paid model service.

## References

- [GitHub Trending](https://github.com/trending)
- [Scheduled workflow limits](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [GitHub Actions billing](https://docs.github.com/en/actions/concepts/billing-and-usage)
- [Repository Contents API](https://docs.github.com/en/rest/repos/contents#get-repository-content)
