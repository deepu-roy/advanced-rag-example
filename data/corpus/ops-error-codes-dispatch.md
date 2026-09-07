---
id: ops-error-codes-dispatch
title: Dispatch Subsystem Error Codes
tags: [ops, engineering, reference]
---
# Dispatch Subsystem Error Codes

This reference lists the error codes raised by the dispatch subsystem of
the transportation management system, along with the most common cause and
first response step for each.

- E-1001 — Duplicate shipment ID: the same shipment was submitted twice
  from the order system. First response: check for a retried webhook
  from the order system before assuming a data error.
- E-1002 — Carrier capacity exceeded: the assigned carrier has no
  remaining capacity for the requested pickup window. First response:
  reassign the shipment to the next carrier in the routing guide.
- E-1050 — Address validation failure: the delivery address could not be
  matched against the postal database. First response: contact the
  customer to confirm the address before dispatch.

Dispatch errors are raised the moment a shipment is tendered, before any
manifest or billing step runs, so they should always be resolved first if
a shipment shows multiple error codes at once.
