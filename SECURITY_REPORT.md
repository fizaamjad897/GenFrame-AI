# SECURITY REPORT — Visual Engine Backend 🔐

**Purpose:** This document provides a comprehensive security assessment for the Visual Engine backend and guidance to secure client integrations that will call its API. It contains threats, impacts, prioritized mitigations, and a remediation checklist you can follow or hand to a security team.

---

## Executive Summary ✅
- The Visual Engine backend processes image uploads, calls third‑party AI services (Google Gemini), stores artifacts in DigitalOcean Spaces, and persists usage and user records in MongoDB.
- The highest risks are **data leakage** (public S3 objects / unprotected tokens), **insecure configuration** (CORS "*", secret handling, import-time failures), **abuse/fraud** (billing exhaustion, DoS), and **third-party exposure** (sending user data to GenAI without controls).
- This report focuses on client-side concerns when calling the API and internal system weaknesses. Each item includes the impact and concrete mitigation steps (short/medium/long-term) and a priority.

---

## Scope & Assumptions
- Scope: `main.py`, `auth.py`, storage (DigitalOcean Spaces), third-party calls (Google Gemini), MongoDB, and public API surface (`/api/...`).
- Assumes deployment on cloud or VPS and client will call the public API (HTTPS) from internal systems.
- Threats from external attackers, malicious or compromised clients, and accidental data leakage are considered.

---

## Threat Model (high level)
- Assets: user images, generated images, client-sensitive images, user credentials, JWT tokens, API keys, billing and usage data, backups.
- Actors: external attackers, rogue clients, malicious insiders, compromised third-party accounts, supply chain threats.
- Typical threat vectors: network interception, misconfigured storage (public buckets), leaked API keys, broken authentication flows, improper input validation (malicious files), DoS and abuse, privacy breaches via third-party AI.

---

## Issues, Impact & Mitigations (Detailed)

### 1) Transport Security (TLS) 🌐
- Risk: TLS not enforced or misconfigured allows MITM, credential theft.
- Impact: Token compromise, credential interception, unauthorized API calls.
- Mitigation:
  - Enforce HTTPS only (redirect HTTP → HTTPS at load balancer).
  - Use strong TLS versions (>= TLS 1.2) and recommended ciphers; enable HSTS.
  - Recommend certificate management (ACME / managed certs) and monitoring for expiry.
- Priority: Critical


### 2) Authentication & JWTs 🔑
- Risk: Weak or leaked `JWT_SECRET`, long token lifetimes, lack of revocation.
- Impact: Stolen tokens allow impersonation and unrestricted resource access.
- Mitigation:
  - Use a strong secret from a secrets manager; do not fallback to hard-coded defaults.
  - Use short access token lifetimes + refresh tokens and token revocation lists (or store token IDs or session records to invalidate tokens).
  - Require secure storage of tokens on client (use key vaults).
  - Document token rotation process and revoke compromised tokens immediately.
- Priority: Critical


### 3) API Keys (server-provided) 🔐
- Risk: Poorly stored or transmitted API keys can be leaked. Raw keys stored in logs or sent repeatedly increase exposure.
- Impact: Compromised API keys can be used to impersonate clients and access sensitive images/data.
- Mitigation:
  - Store only hashed API key values on the server (HMAC-SHA256 or a stronger KDF using a server secret). The server should show the raw key to the client only once at creation.
  - Limit to one active key per user (or allow multiple with rotation policy); require explicit deletion before re-issuance to support key rotation and accidental loss procedures.
  - Accept API keys over an encrypted channel (HTTPS) and require clients to store API keys securely (vaults). Consider mTLS for highly-sensitive integrations.
  - Do not log raw API keys, and rotate the server-side HMAC secret periodically.
- Priority: High


### 4) Password Reset & Email Flow 📧
- Risk: Dev-mode returns reset tokens in responses and prints them; tokens live in DB until used and may be logged.
- Impact: Unauthorized password changes if token leaks, phishing vectors.
- Mitigation:
  - Never return tokens in API responses in production. Use only email-delivered tokens or secure out-of-band channels.
  - Ensure password reset tokens are single-use and TTL-bound (they already expire via TTL index but verify configuration).
  - Rate-limit password reset requests and monitor for enumeration.
- Priority: High


### 5) API Surface & CORS 🧭
- Risk: `CORS(allow_origins=['*'])` allows any origin to request the API from browsers.
- Impact: Cross-origin abuse by malicious web apps; easier to exploit end-users operating within web browsers.
- Mitigation:
  - Restrict `allow_origins` to the client's frontend origins or support runtime allowlists per-client.
  - For machine-to-machine (server-to-server) integrations, prefer API keys, mutual TLS, or client credentials instead of public JWT auth flows.
- Priority: High- Risk: Weak or leaked `JWT_SECRET`, long token lifetimes, lack of revocation.
- Impact: Stolen tokens allow impersonation and unrestricted resource access.
- Mitigation:
  - Use a strong secret from a secrets manager; do not fallback to hard-coded defaults.
  - Use short access token lifetimes + refresh tokens and token revocation lists (or store token IDs or session records to invalidate tokens).
  - Require secure storage of tokens on client (use key vaults).
  - Document token rotation process and revoke compromised tokens immediately.
- Priority: Critical


### 3) Password Reset & Email Flow 📧
- Risk: Dev-mode returns reset tokens in responses and prints them; tokens live in DB until used and may be logged.
- Impact: Unauthorized password changes if token leaks, phishing vectors.
- Mitigation:
  - Never return tokens in API responses in production. Use only email-delivered tokens or secure out-of-band channels.
  - Ensure password reset tokens are single-use and TTL-bound (they already expire via TTL index but verify configuration).
  - Rate-limit password reset requests and monitor for enumeration.
- Priority: High


### 4) API Surface & CORS 🧭
- Risk: `CORS(allow_origins=['*'])` allows any origin to request the API from browsers.
- Impact: Cross-origin abuse by malicious web apps; easier to exploit end-users operating within web browsers.
- Mitigation:
  - Restrict `allow_origins` to the client's frontend origins or support runtime allowlists per-client.
  - For machine-to-machine (server-to-server) integrations, prefer API keys, mutual TLS, or client credentials instead of public JWT auth flows.
- Priority: High


### 5) Public Object Storage (DigitalOcean Spaces) ☁️
- Risk: `ACL='public-read'` and public URL generation results in objects accessible to anyone with the URL.
- Impact: Sensitive client images could be publicly exposed; automated scanners can index them.
- Mitigation:
  - Avoid public-read objects. Use private buckets and generate time-limited signed URLs for access.
  - If public buckets are required, partition namespaces and avoid exposing PII in filenames; implement object lifecycle policies.
  - Apply bucket policies to disallow list/get permissions to anonymous users.
- Priority: Critical


### 6) Secrets Management & Environment Handling 🔐
- Risk: Secrets in `.env`, weak defaults (JWT secret default), and raising on missing envs at import cause fragile configuration.
- Impact: Leaked secrets, accidental leaks via VCS, unauthorized access to third-party services.
- Mitigation:
  - Use a secret manager (AWS Secrets Manager, Azure Key Vault, Google Secret Manager) in production and inject secrets at runtime.
  - Enforce environment validation at startup (require secrets in production), but support safe defaults for local dev.
  - Audit and rotate keys regularly; apply least privilege on API keys.
- Priority: Critical


### 7) Third-party AI usage (Google Gemini) 🤖
- Risk: Client images or prompts may contain sensitive/PIN data that get sent to a third-party model; models may persist or use data per provider term.
- Impact: Sensitive data leakage outside client control; regulatory exposure (PII/PHI) depending on industry.
- Mitigation:
  - Define data classification policies; require explicit client consent before sending sensitive images to the model.
  - Where feasible, implement client-side redaction or client-side preprocessing to remove sensitive areas (blurring), or provide an on-prem variant or private endpoint arrangement (if provider supports it).
  - Review and bind to a Data Processing Agreement (DPA) with the provider; confirm the AI provider's retention/usage policies.
- Priority: Critical


### 8) File Upload Handling & Malware Risk 🗂️
- Risk: Unvalidated uploaded files may contain malicious payloads; PIL vulnerabilities may be triggered by crafted files.
- Impact: RCE or Denial-of-Service on image processing pipeline, resource exhaustion.
- Mitigation:
  - Validate file MIME types and magic bytes; restrict to allowed image types.
  - Enforce size limits and processing timeouts, and run image processing in a sandboxed worker with resource limits.
  - Use up-to-date imaging libraries and scan file content for malicious patterns; consider running uploads through an antivirus/malware scanner.
- Priority: High


### 9) Billing Abuse / Usage Fraud 💳
- Risk: Attackers or misconfigured clients could exhaust credits by automating calls.
- Impact: Unexpected costs and service abuse.
- Mitigation:
  - Enforce per-user and per-API-key rate limits and quotas.
  - Implement anomaly detection (spike detection), and soft-lock accounts pending human review for suspicious usage.
  - Require payment method validation for paid plans and send usage alerts to clients.
- Priority: High


### 10) Logging, Monitoring & Privacy 🕵️
- Risk: Logs may contain PII, tokens, or sensitive image URLs; logs could be publicly accessible or retained too long.
- Impact: Data leakage via logs; compliance and privacy violations.
- Mitigation:
  - Centralize logging, mask or redact sensitive data (tokens, full images, SSNs), and limit log retention per policy.
  - Enable monitoring/alerting for suspicious events (multiple failed logins, spike in usage, new IPs) and forward to SIEM.
  - Protect logs with access control and encryption-at-rest.
- Priority: High


### 11) Database & Backups 🗄️
- Risk: MongoDB left accessible without auth or exposed to public internet; backups unencrypted or accessible.
- Impact: Full data exfiltration, customer PII exposure.
- Mitigation:
  - Bind MongoDB to private network interfaces, require authentication with least-privilege accounts, and enable TLS for DB connections.
  - Encrypt backups, store backups in restricted storage, validate restore procedures as part of disaster recovery planning.
- Priority: Critical


### 12) Rate Limiting & DDoS Protection ⚡
- Risk: No global or per-user rate limiting, or no WAF/anti-DDoS.
- Impact: Service degradation, higher cloud costs, outages.
- Mitigation:
  - Implement rate limits at API gateway or load balancer, WAF rules, and CDN with TLS termination.
  - Use managed DDoS protection if available; monitor metrics and autoscale carefully to avoid runaway costs.
- Priority: High


### 13) CI/CD & Dependency Supply Chain 🔗
- Risk: Unpinned dependencies, dev secrets in CI, and lack of software composition analysis (SCA).
- Impact: Vulnerable libraries exploited; compromised CI injects bad code.
- Mitigation:
  - Pin production dependency versions, run SCA (Dependabot, Snyk), run SAST/DAST in CI, and scan for secrets in commits.
  - Restrict CI secrets and require PR approvals; consider signed commits for releases.
- Priority: High


### 14) Operational & Access Controls 👥
- Risk: Overprivileged developer or operator accounts, no MFA, no RBAC, poor change control.
- Impact: Insider compromise, unauthorized changes, data leaks.
- Mitigation:
  - Enforce MFA for all accounts, apply RBAC, restrict production access (bastion host or jump box), and use ephemeral credentials.
  - Keep an access audit and use Just-In-Time access for sensitive operations.
- Priority: High


### 15) Privacy & Legal / Compliance ⚖️
- Risk: Processing client sensitive images might violate regulations (GDPR, HIPAA) if client data is PII/PHI and there is no DPA or appropriate safeguards.
- Impact: Legal liability, fines, damage to trust.
- Mitigation:
  - Establish DPAs and data processing boundaries with clients and providers.
  - Provide options for data residency, data minimization, and deletion upon request; document retention periods and deletion flows.
- Priority: Critical (for regulated industries)


### 16) Image URLs & Caching 🧾
- Risk: Public URLs leak via CDN caches or referrers. Exposed images may be cached indefinitely at CDNs.
- Impact: Long-term uncontrolled access to sensitive images.
- Mitigation:
  - Use signed URLs with short TTLs for clients; set cache-control headers appropriately; if public assets are necessary, avoid embedding sensitive content.
- Priority: High


### 17) Incrementing Units in Finally Block (Specific code finding) ⚠️
- Risk: Units are incremented in a `finally` block, so failed operations still consume user credits.
- Impact: Unexpected billing and client dissatisfaction.
- Mitigation:
  - Increment units only on successful completion and optionally log failed attempts separately.
- Priority: Medium


---

## Client-specific Guidance (how clients should safely call your API)
1. Use **server-to-server authentication** (API keys, OAuth client credentials, or mTLS) for automated integrations; avoid embedding credentials in client-side JS.
2. Keep secrets in client's secret manager (Key Vault, HashiCorp Vault) and rotate keys periodically.
3. Prefer sending non-sensitive images or anonymized data; if sending sensitive images, obtain a DPA and use encryption at rest and in transit.
4. Use IP allowlisting and VPC peering or private endpoints if high sensitivity.
5. Validate input on their side and employ rate limiting with exponential backoff on errors.
6. Ask for an SLA and clearly define responsibilities for incident notifications, breach handling, and data retention.

---

## Prioritized Remediation Checklist (Quick action items)
- [ ] Fix `@app.get("/api/users/me")` bug and remove stray returns. (Low effort, Critical)
- [ ] Replace `CORS(allow_origins=['*'])` with per-client allowlist or restrict to known frontends. (Low) 
- [ ] Use signed S3 URLs instead of `public-read` and make buckets private. (Medium)
- [ ] Move secret handling to secret manager and remove weak defaults. (High)
- [ ] Ensure TLS everywhere and HSTS (High)
- [ ] Change password reset to not return tokens in responses (High)
- [ ] Implement rate limiting & quotas per user / per API key (High)
- [ ] Ensure MongoDB is not publicly accessible and backups are encrypted (Critical)
- [ ] Add logging redaction, SIEM integration, and alerting for anomalous activity (High)
- [ ] Add automated tests: SAST/SCA, dependency scanning, and scheduled pentesting (Medium)

---

## Operational Recommendations & Roadmap
- Short-term (0-2 weeks): fix public storage policy, CORS, JWT secret, password reset token exposure, unit increment bug, and require TLS.
- Medium-term (2-8 weeks): rate limits, monitoring & alerting, secrets manager, signed URLs, CI pipeline hardening, and SCA.
- Long-term (8+ weeks): dedicated private endpoints or VPC peering for sensitive clients, formal DPA and compliance reviews, periodic pen tests and bug bounty.

---

## Incident Response (IR) Guidance
- Prepare IR playbook with P0/P1 procedures, including:
  - Triage and containment (rotate keys, block compromised accounts)
  - Customer notification windows (obligations vary by regulation; target <72 hours for GDPR)
  - Post-incident forensic analysis, fix, and communication
- Keep contact lists, escalation chains, and sample communication templates ready.

---

## Example Secure Configuration Snippets
- **FastAPI CORS (restrict origins)**
```py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.client.example"],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)
```

- **Signed S3 URL (Python boto3)**
```py
s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucket, 'Key': key},
    ExpiresIn=3600,
)
```

- **Enforce HSTS (proxy or framework)**
```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

---

## Risk Matrix (summary)
| Risk | Likelihood | Impact | Priority |
|------|------------:|-------:|:--------:|
| Public object leaks | High | High | Critical |
| JWT secret fallback | Medium | High | Critical |
| Sending sensitive data to Gemini | Medium | High | Critical |
| CORS open to all | High | Medium | High |
| Password token disclosure (dev-mode) | Medium | High | High |
| Unprotected MongoDB | Low/Medium | High | Critical |
| Rate-limiting missing | High | Medium | High |

---

## Final Notes & Next Steps
- Review this report with the client to identify any regulatory constraints (e.g., HIPAA, GDPR) and adjust mitigations accordingly.
- Prioritize fixes labelled *Critical* and apply them before onboarding clients with sensitive data.
- Offer options for enhanced isolation (VPC peering, on-prem gateway, or custom deployments) and contractual protections (DPA, SOC2/ISO audits) if clients need assurances.

---

If you want, I can: **(a)** implement critical code fixes in the repo now, (b) create tests and CI checks for security, or (c) tailor the report into a shorter executive brief or client-facing SLA / DPA draft. Which would you like me to do next? 

Created by: GitHub Copilot (Raptor mini (Preview))
