---
id: eng-runbook-rollback
title: Rollback Runbook
tags: [engineering, runbook, incident]
---
# Rollback Runbook

If a production deploy causes an error rate spike, a failed health check,
or a customer-visible regression, the on-call engineer should roll back
immediately rather than attempting a forward fix, unless the fix is
trivial and already validated in staging.

To roll back, use the `deploy rollback <service>` command in the deploy
tool, which redeploys the previous release candidate image tagged as that
service's last-known-good rollback point. A rollback does not require a
second engineer's approval, unlike a normal deploy, because reverting to a
previously-approved release carries less risk than shipping something new.

After a rollback, the on-call engineer posts in `#incidents` with the
service name, the rollback point used, and a link to the metrics that
triggered the decision. A rollback that resolves the issue still requires
a postmortem if it affected customers for more than five minutes; see the
postmortem process for the follow-up steps.
