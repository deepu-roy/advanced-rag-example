---
id: eng-oncall-escalation
title: On-Call Escalation Policy
tags: [engineering, oncall, incident]
---
# On-Call Escalation Policy

Software and systems incidents page the on-call engineer through the
on-call tool, regardless of the time of day, based on the severity of the
triggering alert. Sev1 (customer-facing outage) and Sev2 (major
degradation) alerts page immediately; Sev3 and below are queued for the
next business day unless they cross a threshold that auto-escalates them.

If the primary on-call engineer does not acknowledge a page within 5
minutes, it escalates automatically to the secondary on-call engineer for
that team, and after another 5 minutes, to the engineering manager on
the escalation roster. This escalation chain runs identically at 3pm or
3am — there is no reduced on-call coverage overnight.

Any Sev1 incident automatically opens an incident channel and pages the
incident commander on-call rotation, separate from the service-owning
team's on-call, so that a single engineer is never solely responsible for
both fixing the issue and coordinating communication during a major
outage.
