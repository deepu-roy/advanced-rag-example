---
id: product-api-rate-limits
title: Customer API Rate Limits
tags: [product, api, reference]
---
# Customer API Rate Limits

The customer-facing shipments API enforces a rate limit of 120 requests
per minute per API key on the `/shipments` endpoint, and 300 requests per
minute on the read-only `/tracking` endpoint. Limits are enforced using a
sliding one-minute window, not a fixed per-minute bucket.

When a client exceeds its rate limit, the API returns an HTTP 429
response with a `Retry-After` header indicating how many seconds to wait
before retrying. Clients that repeatedly ignore the `Retry-After` header
and continue sending requests may have their API key temporarily
suspended for one hour.

A separate HTTP 503 response indicates the API is temporarily unable to
serve requests due to an upstream dependency issue, rather than rate
limiting — 503 responses should be retried with exponential backoff, while
429 responses should be retried only after the `Retry-After` interval.
Enterprise customers may request a higher rate limit by contacting their
account manager; increases are provisioned per API key, not account-wide.
