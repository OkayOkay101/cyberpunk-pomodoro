const fs = require('fs');
const path = require('path');
const assert = require('assert');

module.exports = function assertWeeklyFocusAccessibility() {
  const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
  assert.match(html, /id="weeklyFocusChart" role="group" aria-label="เวลาที่โฟกัสในแต่ละวันของสัปดาห์"/);
  assert.match(html, /item\.setAttribute\('role', 'group'\)/);
  assert.match(html, /item\.setAttribute\('aria-label', `\$\{day\.date\}: \$\{day\.minutes\} นาที`\)/);
};
