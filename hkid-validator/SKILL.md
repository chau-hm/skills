---
name: hkid-validator
description: Validate and format Hong Kong Identity Card (HKID) numbers with checksum logic, including bracketed/non-bracketed input normalization and masked output. Use when users ask to verify HKID validity, parse HKID check digits, mask HKID values, or convert legacy HKID validation code into reusable scripts.
---

# HKID Validator

Use the bundled Node.js script for deterministic HKID validation.

## Run validation from CLI

```bash
node skills/hkid-validator/scripts/validate_hkid.mjs <HKID>
```

Examples:

```bash
node skills/hkid-validator/scripts/validate_hkid.mjs A1234563
node skills/hkid-validator/scripts/validate_hkid.mjs "A123456(3)"
```

Output is JSON with:

- `input`
- `normalized`
- `isValid`
- `hkid`
- `checkDigit`
- `masked`

## Reuse as module

Import from:

- `skills/hkid-validator/scripts/validate_hkid.mjs`

Functions:

- `normalizeHkid(raw)`
- `validateHkid(raw)`
