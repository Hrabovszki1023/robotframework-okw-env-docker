# OKW Environment Provider Contract (Specification)

This document defines the **provider-neutral contract** implemented by:

- robotframework-okw-env-proxmox
- robotframework-okw-env-docker

Both libraries MUST expose the same Robot Framework keyword API and semantics.
Implementation details (Proxmox vs Docker) are explicitly out of scope.

## Core Concepts

### Environment
An **Environment** is an isolated, disposable test runtime (tenant/worker scoped). It may consist of VMs (Proxmox) or containers (Docker), but MUST behave the same from the test's perspective.

### Tenant / Worker Isolation
Each test execution must run in an isolated environment.

Recommended tenant id format:

TENANT_ID = <run_id>__<worker_id>

Provider must use TENANT_ID as join key for:
- resources (VMs/containers/networks)
- cleanup
- outputs

### Outputs
Providers MUST publish environment outputs in a provider-neutral key space.
Outputs MUST be retrievable via `Get Output` and listable via `List Outputs`.

Example keys:
- web.base_url
- web.host
- web.port
- db.host
- db.port
- env.id

### Template Rendering
Providers MUST support resolving `{{...}}` tokens in arbitrary strings using the current environment context.

Token format:
- `{{web.base_url}}`
- `{{db.host}}`

Unknown tokens MUST fail deterministically (see errors).

## Error Handling (Deterministic)
Providers MUST fail with clear, deterministic errors.

Recommended error prefixes (MUST be stable strings):
- `OKWENV:NOT_ACQUIRED` (no active environment)
- `OKWENV:INVALID_STATE`
- `OKWENV:UNKNOWN_OUTPUT`
- `OKWENV:TEMPLATE_ERROR`
- `OKWENV:PROVISIONING_FAILED`
- `OKWENV:TIMEOUT`

## Lifecycle Semantics (Postcondition-first)

Providers MUST be "postcondition-first":
- Keywords assert their postcondition, perform actions until satisfied, or fail deterministically.

Example:
- `Ensure Environment Ready` MUST return only if environment is ready.

## Keyword Contract (MVP)
The following keywords MUST exist and MUST be supported:

1. Acquire Environment
2. Release Environment
3. Get Output
4. Render Template
5. List Outputs
6. Get Environment Id
7. Ensure Environment Ready
8. Reset Environment
9. Describe Environment
10. Validate Environment State

## Keyword Idempotency
- `Ensure Environment Ready` MUST be idempotent.
- `Validate Environment State` MUST be idempotent.
- `Describe Environment` MUST be read-only.
- `List Outputs` MUST be read-only.
- `Get Output` MUST be read-only.
- `Release Environment` MUST be safe to call multiple times (second call may be a no-op).

## Minimal State Model
Provider MUST track an internal state at minimum:

- not_acquired
- acquired (provisioning in progress or done)
- ready
- released

Transitions:
- Acquire Environment: not_acquired -> acquired -> ready (or fail)
- Release Environment: any -> released
- Reset Environment: ready -> ready (re-provision/clean)
