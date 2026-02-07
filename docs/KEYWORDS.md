# Keyword Reference (OKW Env Provider)

This reference MUST be identical across provider implementations.

## Acquire Environment
**Purpose:** Allocate and provision an isolated environment for the current run/worker.

**Arguments (recommended):**
- `tenant_id` (optional; provider may derive from context)
- `definition` (optional; YAML path/string)
- `timeout` (optional)

**Postcondition:**
- environment state is `ready`
- outputs are available

**Errors:**
- OKWENV:PROVISIONING_FAILED
- OKWENV:TIMEOUT
- OKWENV:INVALID_STATE

---

## Release Environment
**Purpose:** Tear down environment and free all resources.

**Postcondition:**
- resources are released
- internal state is `released`

**Idempotent:** yes (safe to call multiple times)

---

## Get Output
**Purpose:** Return a single output value by key.

**Arguments:**
- `key` (required)

**Returns:**
- string value

**Errors:**
- OKWENV:NOT_ACQUIRED
- OKWENV:UNKNOWN_OUTPUT

---

## Render Template
**Purpose:** Replace `{{...}}` tokens in a string using current outputs.

**Arguments:**
- `template` (required)

**Returns:**
- rendered string

**Errors:**
- OKWENV:NOT_ACQUIRED
- OKWENV:TEMPLATE_ERROR
- OKWENV:UNKNOWN_OUTPUT

---

## List Outputs
**Purpose:** List all available output keys.

**Returns:**
- list of strings (keys)

**Errors:**
- OKWENV:NOT_ACQUIRED

---

## Get Environment Id
**Purpose:** Return provider-neutral environment id (tenant id).

**Returns:**
- string id

**Errors:**
- OKWENV:NOT_ACQUIRED

---

## Ensure Environment Ready
**Purpose:** Wait/verify that environment is ready.

**Arguments (recommended):**
- `timeout` (optional)

**Postcondition:**
- environment state is `ready`

**Idempotent:** yes

**Errors:**
- OKWENV:NOT_ACQUIRED
- OKWENV:TIMEOUT
- OKWENV:INVALID_STATE

---

## Reset Environment
**Purpose:** Reset environment to a clean baseline (reprovision or cleanup).

**Postcondition:**
- environment remains `ready`
- baseline restored

**Errors:**
- OKWENV:NOT_ACQUIRED
- OKWENV:PROVISIONING_FAILED
- OKWENV:TIMEOUT

---

## Describe Environment
**Purpose:** Return a human-readable description (provider-neutral fields preferred).

**Returns:**
- string (multiline allowed) OR dict-like string

**Read-only:** yes

**Errors:**
- OKWENV:NOT_ACQUIRED

---

## Validate Environment State
**Purpose:** Validate that environment matches declared model/definition.

**Returns:**
- nothing (pass/fail)

**Idempotent:** yes

**Errors:**
- OKWENV:NOT_ACQUIRED
- OKWENV:INVALID_STATE
