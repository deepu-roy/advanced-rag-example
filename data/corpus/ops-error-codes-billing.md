---
id: ops-error-codes-billing
title: Billing Subsystem Error Codes
tags: [ops, engineering, reference]
---
# Billing Subsystem Error Codes

This reference lists the error codes raised by the billing subsystem of
the transportation management system, along with the most common cause and
first response step for each.

- E-5010 — Rate mismatch: the billed rate does not match the contracted
  rate card on file. First response: escalate to the carrier billing team
  before approving payment.
- E-5011 — Missing accessorial charge code: an invoice line item cannot be
  matched to a known accessorial charge type. First response: return the
  invoice to the carrier for a corrected charge code.
- E-5020 — Duplicate invoice number: the carrier submitted an invoice
  number that has already been paid. First response: hold payment and
  confirm with the carrier whether this is a resubmission or a new charge.

Billing errors are evaluated during invoice reconciliation, after a
shipment has already been delivered, so they never block an active
shipment — only its final payment.
