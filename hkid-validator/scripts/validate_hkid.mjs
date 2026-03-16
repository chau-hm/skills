#!/usr/bin/env node

/**
 * Normalize HKID input into: { body, checkDigit, normalized }
 * Accepted formats:
 * - A123456(7)
 * - AB123456(7)
 * - A1234567
 * - AB1234567
 */
export function normalizeHkid(raw) {
  if (raw == null) {
    return { body: '', checkDigit: '', normalized: '' };
  }

  const input = String(raw).trim().toUpperCase();
  const match = input.match(/^([A-Z]{1,2}[0-9]{6})\(?([0-9A])\)?$/);

  if (!match) {
    return { body: '', checkDigit: '', normalized: input };
  }

  const body = match[1];
  const checkDigit = match[2];
  return { body, checkDigit, normalized: `${body}${checkDigit}` };
}

/**
 * Validate HKID checksum.
 * Rule follows legacy implementation:
 * - One-letter prefix uses leading space (value 36)
 * - Letters map A=10 ... Z=35
 * - Weighted sum by positions 9..1, valid if sum % 11 === 0
 */
export function validateHkid(raw) {
  const { body, checkDigit, normalized } = normalizeHkid(raw);

  if (!body || !checkDigit) {
    return {
      input: raw,
      normalized,
      isValid: false,
      hkid: '',
      checkDigit: '',
      masked: ''
    };
  }

  let id = `${body}${checkDigit}`;
  if (id.length === 8) {
    // one-letter prefix, prepend space for checksum calculation
    id = ` ${id}`;
  }

  let checksum = 0;
  for (let i = 0; i < id.length; i++) {
    const ch = id[i];
    const weight = 9 - i;

    if (/[A-Z]/.test(ch)) {
      checksum += (ch.charCodeAt(0) - 55) * weight;
    } else if (ch === ' ') {
      checksum += 36 * weight;
    } else if (/[0-9]/.test(ch)) {
      checksum += Number(ch) * weight;
    } else {
      return {
        input: raw,
        normalized,
        isValid: false,
        hkid: body,
        checkDigit,
        masked: ''
      };
    }
  }

  const isValid = checksum % 11 === 0;
  const masked = isValid ? `${body.slice(0, Math.max(0, body.length - 3))}XXX(X)` : '';

  return {
    input: raw,
    normalized,
    isValid,
    hkid: body,
    checkDigit,
    masked
  };
}

function runCli() {
  const arg = process.argv[2];
  if (!arg) {
    console.error('Usage: node validate_hkid.mjs <HKID>');
    process.exit(1);
  }

  const result = validateHkid(arg);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exit(result.isValid ? 0 : 2);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runCli();
}
