---
id: eng-postmortem-process
title: Incident Postmortem Process
tags: [engineering, incident, process]
---
# Incident Postmortem Process

Every Sev1 or Sev2 incident, and any Sev3 incident that affected customers
for more than five minutes, requires a written postmortem within three
business days of resolution. The postmortem is owned by the incident
commander, not necessarily the engineer who fixed the issue.

The postmortem document follows a fixed structure: a timeline of events
from detection to resolution, the customer-facing impact in concrete
terms (duration, number of affected customers or shipments), a root-cause
analysis using the "five whys" technique, and a list of concrete follow-up
action items, each with an owner and a due date.

Postmortems are blameless by policy: the document focuses on what allowed
the failure to happen and propagate, not on which individual made a
mistake. A completed postmortem is reviewed in the weekly engineering
review meeting, and its action items are tracked to completion the same
way any other engineering work is tracked.
