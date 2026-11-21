#!/usr/bin/env bash
# commit and push data/public + docs/jx_runs progress, rebasing over concurrent pushes
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add data/public data/shadow docs/jx_runs
git diff --cached --quiet && exit 0
git commit -qm "fetch liquidations: $1 progress ($(date -u +%FT%TZ))"
for i in 1 2 3 4 5 6; do
  git pull --rebase --no-edit origin "${GITHUB_REF_NAME}" && git push origin "HEAD:${GITHUB_REF_NAME}" && exit 0
  sleep $((i * 7))
done
exit 1
