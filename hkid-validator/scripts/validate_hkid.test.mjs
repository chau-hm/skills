import test from 'node:test';
import assert from 'node:assert/strict';
import { validateHkid } from './validate_hkid.mjs';

const positiveCases = ['A1234563'];
const negativeCases = ['A1234567'];

test('positive HKID cases should validate', () => {
  for (const hkid of positiveCases) {
    const result = validateHkid(hkid);
    assert.equal(result.isValid, true, `${hkid} should be valid`);
  }
});

test('negative HKID cases should fail validation', () => {
  for (const hkid of negativeCases) {
    const result = validateHkid(hkid);
    assert.equal(result.isValid, false, `${hkid} should be invalid`);
  }
});

test('accept bracket format as equivalent input', () => {
  const result = validateHkid('A123456(3)');
  assert.equal(result.isValid, true);
  assert.equal(result.normalized, 'A1234563');
});

