/** Read a thrown error message without assuming every rejection is an Error. */
export function errorMessage(value: unknown): string {
	return typeof value === 'object' &&
		value !== null &&
		'message' in value &&
		typeof value.message === 'string'
		? value.message
		: '';
}

/** Preserve HTTP conflict handling for API errors and structured rejections. */
export function errorStatus(value: unknown): number | undefined {
	return typeof value === 'object' &&
		value !== null &&
		'status' in value &&
		typeof value.status === 'number'
		? value.status
		: undefined;
}
