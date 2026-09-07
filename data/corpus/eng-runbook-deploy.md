---
id: eng-runbook-deploy
title: Deploy Runbook
tags: [engineering, runbook, deploy]
---
# Deploy Runbook

Deploys to production run through the standard pipeline: a merge to `main`
triggers CI, which runs the test suite and, on success, builds a release
candidate image. A release is promoted to production only after an
engineer other than the author approves the pull request and the release
candidate passes a smoke test in staging.

Deploys are scheduled during the daily deploy window (10am-4pm on the
deploying team's local time, weekdays only) unless the change is a
critical fix, which may deploy outside the window with on-call approval.
Each production deploy is announced in the `#deploys` channel before and
after it completes, including the release version and a link to the
changeset.

Every deploy is automatically tagged with a rollback point, and the
on-call engineer is expected to actively watch key dashboards for 15
minutes after any production deploy before considering it stable.
