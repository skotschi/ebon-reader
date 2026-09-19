const { test } = require('node:test');
const assert = require('node:assert/strict');
const { issueNumbers, gate } = require('./policy.cjs');
const repo = 'skotschi/ebon-reader';
const pr = (body, base = 'dev', head = 'feature/1-work', full_name = repo) =>
  ({ body, base: { ref: base }, head: { ref: head, repo: { full_name } } });
test('issue references distinguish real content from template placeholders', () => {
  assert.deepEqual(issueNumbers(pr('Closes #12\nRefs #13'), repo), [12, 13]);
  for (const body of ['', '<!-- Closes #12 -->', '```\nCloses #12\n```', 'Closes other/repo#12']) {
    assert.throws(() => issueNumbers(pr(body), repo));
  }
});
test('only same-repository dev can promote to main', () => {
  assert.deepEqual(issueNumbers(pr('', 'main', 'dev'), repo), []);
  assert.throws(() => issueNumbers(pr('Closes #1', 'main'), repo));
  assert.throws(() => issueNumbers(pr('', 'main', 'dev', 'other/fork'), repo));
  assert.throws(() => issueNumbers(pr('Closes #1', 'other'), repo));
});
test('gate rejects missing, skipped, failed and cancelled required jobs', () => {
  const result = Object.fromEntries(['policy', 'validation', 'backend', 'frontend', 'security', 'desktop'].map(k => [k, { result: 'success' }]));
  gate(result, true);
  for (const name of Object.keys(result)) {
    for (const state of ['failure', 'cancelled', 'skipped', undefined]) {
      assert.throws(() => gate({ ...result, [name]: { result: state } }, true));
    }
  }
  gate({ ...result, desktop: { result: 'skipped' } }, false);
  assert.throws(() => gate(result, false));
});
