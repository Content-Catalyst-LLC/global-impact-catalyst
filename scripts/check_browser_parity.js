#!/usr/bin/env node
'use strict';
const fs=require('fs'); const path=require('path');
const core=require(path.resolve(__dirname,'../wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js'));
const dir=path.resolve(__dirname,'../contracts/fixtures'); let checked=0;
for (const filename of fs.readdirSync(dir).filter(n=>n.endsWith('.json')).sort()) {
  const fixture=JSON.parse(fs.readFileSync(path.join(dir,filename),'utf8'));
  const actual=core.buildImpactContract(fixture.input,fixture.generated_at);
  if (JSON.stringify(actual)!==JSON.stringify(fixture.expected)) {
    console.error(`Browser parity failed: ${filename}`);
    console.error('Expected:',JSON.stringify(fixture.expected,null,2));
    console.error('Actual:',JSON.stringify(actual,null,2)); process.exit(1);
  }
  checked++;
}
console.log(`Browser contract parity passed for ${checked} canonical fixtures.`);
