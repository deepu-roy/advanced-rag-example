---
id: it-mfa-sso-policy
title: MFA and Single Sign-On Policy
tags: [it, security, policy]
---
# MFA and Single Sign-On Policy

All internal applications are accessed through single sign-on (SSO), and
every SSO login requires multi-factor authentication (MFA). Northbridge
supports three MFA methods: a push notification through the Okta Verify
app (preferred), a time-based one-time passcode (TOTP) from an
authenticator app, and a physical security key (FIDO2/WebAuthn) for
employees who handle production infrastructure or customer financial data.

SMS-based text message codes are not supported as an MFA method, because
they are vulnerable to SIM-swapping attacks. Employees who lose access to
their MFA method should contact IT Security directly for identity
verification and re-enrollment; self-service MFA reset is intentionally
disabled for security reasons.

Employees with access to production systems or the finance systems tier
are required to enroll a physical security key within 30 days of gaining
that access, in addition to their existing MFA method, so that a lost
phone alone can never lock them out of a security-critical system.
