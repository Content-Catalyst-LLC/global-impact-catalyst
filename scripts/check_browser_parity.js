#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const core = require(path.resolve(__dirname, '../wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js'));
const fixturesDirectory = path.resolve(__dirname, '../contracts/fixtures');
let checked = 0;

for (const filename of fs.readdirSync(fixturesDirectory).filter((name) => name.endsWith('.json')).sort()) {
  const fixture = JSON.parse(fs.readFileSync(path.join(fixturesDirectory, filename), 'utf8'));
  const actual = core.buildImpactRecord(fixture.input, fixture.generated_at);
  const expected = fixture.expected;
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    console.error(`Browser parity failed: ${filename}`);
    console.error('Expected:', JSON.stringify(expected, null, 2));
    console.error('Actual:', JSON.stringify(actual, null, 2));
    process.exit(1);
  }
  checked += 1;
}
console.log(`Browser contract parity passed for ${checked} fixtures.`);
