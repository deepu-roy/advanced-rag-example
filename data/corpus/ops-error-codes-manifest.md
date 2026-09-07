---
id: ops-error-codes-manifest
title: Manifest Sync Subsystem Error Codes
tags: [ops, engineering, reference]
---
# Manifest Sync Subsystem Error Codes

This reference lists the error codes raised by the manifest sync subsystem
of the transportation management system, along with the most common cause
and first response step for each.

- E-4020 — Manifest sync timeout: the nightly sync to a carrier's system
  did not complete before the cutoff. First response: rerun the sync job
  manually and confirm it completes before the next dispatch cycle.
- E-4021 — Stale carrier manifest: the nightly carrier manifest sync
  failed to refresh before dispatch, so committed capacity in the
  dispatch system no longer matches the carrier's actual available
  capacity. First response: force a manifest refresh and re-validate every
  shipment dispatched since the last successful sync.
- E-4022 — Manifest checksum mismatch: the carrier's manifest file was
  corrupted in transit. First response: request a re-send from the
  carrier's EDI gateway rather than retrying the same file.

Manifest sync errors run on a nightly schedule, separate from the
real-time dispatch and billing subsystems, so a manifest error does not
necessarily mean anything is wrong with a specific shipment yet — it means
the carrier's capacity data itself may be out of date.
