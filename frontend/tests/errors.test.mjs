import assert from 'node:assert/strict';
import { test } from 'node:test';
import { errorMessage, errorStatus } from '../src/lib/utils/errors.ts';

test('error messages preserve Error and structured API rejections', () => {
	assert.equal(errorMessage(new Error('Import failed')), 'Import failed');
	assert.equal(errorMessage({ message: 'Conflict', status: 409 }), 'Conflict');
	for (const value of [null, undefined, 'failure', 42, {}, { message: 42 }]) {
		assert.equal(errorMessage(value), '');
	}
});

test('HTTP conflict detection accepts only numeric status values', () => {
	assert.equal(errorStatus({ status: 409 }), 409);
	assert.equal(errorStatus(Object.assign(new Error('Duplicate'), { status: 409 })), 409);
	for (const value of [null, undefined, 'failure', {}, { status: '409' }]) {
		assert.equal(errorStatus(value), undefined);
	}
});
