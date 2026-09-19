const { gate } = require('./policy.cjs');
gate(JSON.parse(process.env.RESULTS), process.env.DESKTOP === 'true');
