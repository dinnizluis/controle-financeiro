# Authentication and Secure Publishing Plan

**Date**: 2026-08-01

## Context

The product direction changed after confirming that the application can be published with
Streamlit. That changes the security posture of the project immediately.

The current application manages highly sensitive personal financial data. Once the app is exposed
through a public URL, running without identity verification is no longer acceptable, even for an
MVP.

This plan records the minimum safe direction for publishing:

- authentication becomes a pre-deployment requirement;
- deployment security is treated as product scope, not infrastructure detail;
- the application remains single-dataset until explicit multi-user isolation is designed.

This plan supersedes the earlier assumption in the MVP foundation plan that authentication could
remain out of scope during the first usable published version.

## Current State

What exists today:

- Streamlit application with no login gate.
- Single SQLite database backing one shared dataset.
- No user model, no per-user authorization rules, and no audit trail.
- App initialization opens the service directly and assumes the viewer is trusted.

Implication:

- the current application is suitable only for local execution or tightly controlled private use;
- publishing the current app without changes would expose financial data to anyone who can open
  the URL;
- adding a generic username and password inside SQLite would be a weak direction compared with the
  native Streamlit authentication model.

## Target State

Publish a Streamlit application that requires verified identity before any financial data is
loaded or rendered.

### Authentication Proposal

Recommended approach for the next published version:

1. Use Streamlit native OIDC authentication with `st.login()`, `st.user`, and `st.logout()`.
2. Configure one external identity provider rather than storing passwords inside the app.
3. Add an explicit authorization allowlist after login, based on stable user claims.
4. Block all data access until the user is both authenticated and authorized.
5. Keep the first published version single-owner or single-household only.

Why this is the preferred option:

- it uses the framework's supported login flow instead of a homegrown credential system;
- it avoids storing password hashes, reset flows, and credential recovery logic in this codebase;
- it fits the current Streamlit architecture with minimal UI disruption;
- it reduces implementation risk while still meeting the critical privacy requirement.

### Identity Provider Recommendation

Default recommendation:

1. Use Google Identity if the app is for personal use by a small known set of accounts.
2. Use Microsoft Entra ID or Auth0 if stricter enterprise-style control is needed later.

Selection criteria:

- personal single-user deployment: Google is usually the lowest-friction choice;
- multi-account family or shared administration: choose a provider that supports easier account
  governance and deprovisioning;
- if future organizational access control matters, prefer Microsoft Entra ID or Auth0 earlier.

### Authorization Model

Authentication alone is insufficient. The application must also decide who is allowed to see the
dataset.

Proposed first-step authorization model:

1. Maintain an allowlist of approved emails or subject identifiers in secrets or environment
   configuration.
2. Deny access to authenticated users who are not explicitly allowlisted.
3. Show a minimal access-denied screen with no financial metadata.
4. Log only non-sensitive diagnostic information for denied access events.

Important limitation:

- because the current repository serves a single shared SQLite dataset, every authorized user would
  see the same financial records;
- therefore the first deployment should authorize only the owner, or a deliberately tiny trusted
  group that is expected to share one dataset.

### Session and Privacy Hardening

The login implementation should include the following hardening rules:

1. Do not initialize the budget service before authentication and authorization succeed.
2. Do not render summary metrics, cycle names, or counts for anonymous users.
3. Add a visible logout action.
4. Check token expiration data from `st.user` and force `st.logout()` when the app considers the
   session expired.
5. Prefer an identity-provider prompt policy that requires fresh account confirmation for sensitive
   sessions when supported.
6. Keep all client secrets and cookie secrets outside version control in Streamlit secrets.
7. Avoid exposing tokens in the UI, logs, or error messages.

### Non-Goals of This Plan

This plan does not yet introduce:

1. self-service signup;
2. password reset flows;
3. role-based access control beyond a simple allowlist;
4. per-user data partitioning;
5. shared household collaboration with separate permissions;
6. full audit/compliance features.

## Architectural Direction

### Recommended Published Architecture

- App: Streamlit with native OIDC authentication.
- Identity: one configured OIDC provider.
- Authorization: local allowlist from secrets or environment variables.
- Persistence: existing SQLite only for the first single-owner deployment.
- Secrets: `.streamlit/secrets.toml` in local development and platform secret management in hosted
  deployment.

### Guardrails

1. Do not build custom password storage in SQLite for the published MVP.
2. Do not treat authentication as complete without authorization.
3. Do not expand to multiple unrelated users until data isolation exists.
4. Do not publish production data while the app still opens anonymous sessions.

### Follow-on Architecture if Multi-User Becomes Necessary

If the product later needs more than one isolated user, create a dedicated feature plan with at
least:

1. user identity mapping table;
2. ownership column or equivalent user scope on each financial record;
3. migration strategy for existing local data;
4. repository and service-level filtering by authenticated principal;
5. regression tests for cross-user data isolation.

## Incremental Milestones

### Milestone 1: Access Gate Before Rendering

Goal: make anonymous access impossible.

Target outcomes:

1. Login screen appears before any financial content.
2. Service initialization happens only after successful auth checks.
3. Anonymous sessions cannot inspect financial data.

### Milestone 2: Authorization and Secrets Handling

Goal: restrict access to explicitly approved identities.

Target outcomes:

1. Allowlist validation is enforced after login.
2. Secrets are loaded only from Streamlit/platform secret stores.
3. Unauthorized but authenticated users receive a clean denial path.

### Milestone 3: Session Hardening and Regression Coverage

Goal: reduce the risk of stale authenticated sessions and deployment regressions.

Target outcomes:

1. Logout flow is visible and working.
2. Expired identities are forced out of the app.
3. UI regression coverage exists for anonymous, unauthorized, and authorized states.

### Milestone 4: Publishing Readiness

Goal: publish with explicit operational controls.

Target outcomes:

1. Hosted secrets are configured correctly for the deployment URL.
2. Redirect URI and cookie secret are valid for the target host.
3. Production deployment checklist includes auth verification before loading real data.

## Backlog Seed

Recommended refined backlog themes derived from this plan:

1. Streamlit OIDC login gate.
2. Authorized-user allowlist and denial state.
3. Protected service initialization and app shell.
4. Session expiry and logout behavior.
5. Deployment secret configuration and publishing checklist.
6. Multi-user isolation discovery spike, if future sharing becomes necessary.

## Dependencies and Risks

### Primary Dependencies

1. Streamlit authentication support enabled in the deployed runtime.
2. One configured OIDC identity provider.
3. Secure secret storage for local and hosted environments.
4. Stable deployment URL so redirect URIs can be registered correctly.

### Main Risks and Mitigations

1. Risk: login is added, but all authorized users still share the same dataset.
   Mitigation: explicitly limit the first published version to a single owner or trusted shared
   household until user-scoped data exists.
2. Risk: secrets leak through version control or logs.
   Mitigation: keep secrets only in Streamlit/platform secret stores and never print them.
3. Risk: session cookies remain usable longer than desired for sensitive data.
   Mitigation: check token expiration claims and force logout according to the app's policy.
4. Risk: auth is implemented after data initialization, leaking metadata before the login gate.
   Mitigation: place authentication and authorization checks before service creation and UI
   rendering.
5. Risk: deployment proceeds because the app works locally, but redirect URIs fail in production.
   Mitigation: make hosted redirect validation a publishing-readiness checkpoint.

## Validation Strategy

This plan is only successful if publication becomes materially safer, not just cosmetically gated.

Validation criteria:

1. Anonymous users cannot reach any financial screen.
2. Authenticated but unauthorized users cannot load financial data.
3. Authorized users can complete the current monthly workflow after login.
4. Logout returns the app to a non-sensitive entry state.
5. Regression tests cover anonymous, denied, and allowed UI states.
6. Deployment secrets and redirect URIs are verified in the target host before real data is used.

## Immediate Next Steps

1. Refine a dedicated authentication backlog item with `/speckit.refine`.
2. Create a feature spec for the login gate and authorization rules before implementation.
3. Decide the first identity provider: Google for personal use, or Microsoft/Auth0 for stricter
   control.
4. Treat deployment of real personal data as blocked until Milestones 1 through 3 are complete.

## Superseded Plans or Related Specs

- Foundation roadmap: [docs/evolution/2026-07-31-mvp-foundation-plan.md](2026-07-31-mvp-foundation-plan.md)
- Evolution index: [docs/evolution/README.md](README.md)
- Cross-feature evolution index: [specs/evolution/README.md](../../specs/evolution/README.md)

This plan adds the minimum security direction required for a published version of the application.
It should be used as the reference whenever deployment, access control, or data exposure tradeoffs
are discussed.