---
id: product-tms-overview
title: Transportation Management System Overview
tags: [product, tms, reference]
---
# Transportation Management System Overview

The transportation management system (TMS) is the internal platform used
to plan, tender, and track shipments across all carriers. It ingests
orders from the order management system, applies routing rules to select
a carrier and service level, tenders the shipment to that carrier, and
tracks status updates through delivery.

Core TMS modules include routing (carrier and mode selection), tendering
(sending the shipment to the chosen carrier via EDI or API), tracking
(ingesting status updates and exceptions), and settlement (matching
carrier invoices against contracted rates before approving payment).

The TMS is the system of record for shipment status and is the system that
raises the dispatch and manifest-sync error codes documented separately in
the operations error code reference. Most day-to-day ops work — filing
delivery exceptions, reassigning carriers, reviewing manifests — happens
inside the TMS rather than in any other internal tool.
