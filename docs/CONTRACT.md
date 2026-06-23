# OKW Environment Provider Contract

This repository implements the **OKW Environment Provider Contract**.

## Contract Files (Authoritative)
The following files define the contract and MUST be kept identical across all
OKW environment provider implementations:

- `docs/SPECIFICATION.md`
- `docs/KEYWORDS.md`
- `tests/contract/contract.robot`

## Rules
1. Any change to the contract files MUST be applied identically to:
   - robotframework-okw-env-proxmox
   - robotframework-okw-env-docker
2. Contract tests MUST pass (`tests/contract/contract.robot`).
3. Breaking the contract requires an explicit, documented decision.

## Rationale
The contract ensures:
- provider interchangeability
- test provider neutrality
- deterministic behavior
- low noise and high signal in test automation

The contract is part of the product, not an optional guideline.

## OKW Global Tokens

This library follows the OKW Global Token Model (defined in `okw-contract-utils`).

Tokens:
- `$IGNORE` (control): supported
- `$EMPTY` (value-intent): supported
- `$DELETE` (action-intent): not supported

Notes:
- `${IGNORE}` / `${EMPTY}` / `${DELETE}` are Robot variables and must be defined by the user if used.
  Recommended:
  ```robot
  *** Variables ***
  ${IGNORE}    $IGNORE
  ${EMPTY}     $EMPTY
  ${DELETE}    $DELETE
  ```

Tokens are evaluated after value expansion (e.g. $MEM{...}), if applicable.

Für Bibliotheken, die `$DELETE` können (GUI), setzt du „supported“.
