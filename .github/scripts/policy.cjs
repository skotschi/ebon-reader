// All PR text is data. Never interpolate it into a shell command.
function issueNumbers(pr, repository) {
  if (pr.base.ref === 'main') {
    if (pr.head.ref !== 'dev' || pr.head.repo?.full_name !== repository) {
      throw new Error('Only same-repository dev promotion PRs may target main.');
    }
    return [];
  }
  if (pr.base.ref !== 'dev') throw new Error('Task PRs must target dev.');
  const body = (pr.body || '').replace(/<!--[\s\S]*?-->/g, '').replace(/```[\s\S]*?```/g, '');
  const ids = [...body.matchAll(/\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+#([1-9]\d*)\b/gi)]
    .map(match => Number(match[1]));
  if (!ids.length) throw new Error('Include Closes #N or Refs #N for a repository issue.');
  return [...new Set(ids)];
}
function gate(results, desktopRequired) {
  const required = ['policy', 'validation', 'backend', 'frontend', 'security'];
  for (const name of required) {
    if (results[name]?.result !== 'success') throw new Error(`${name} did not succeed`);
  }
  if (desktopRequired ? results.desktop?.result !== 'success' : results.desktop?.result !== 'skipped') {
    throw new Error('Desktop job has an unexpected result');
  }
}
module.exports = { issueNumbers, gate };
