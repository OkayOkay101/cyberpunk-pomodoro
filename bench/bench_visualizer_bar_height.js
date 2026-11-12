const { performance } = require('perf_hooks');

const dataArray = Uint8Array.from({ length: 32 }, (_, index) => (index * 37) % 256);
const canvasHeight = 100;

function baselineHeights() {
  let checksum = 0;
  for (let i = 0; i < dataArray.length; i++) {
    const barHeight = (dataArray[i] / 255) * canvasHeight;
    checksum += barHeight;
  }
  return checksum;
}

const barHeights = Float64Array.from({ length: 256 }, (_, value) => (value / 255) * canvasHeight);
function lookupHeights() {
  let checksum = 0;
  for (let i = 0; i < dataArray.length; i++) {
    const barHeight = barHeights[dataArray[i]];
    checksum += barHeight;
  }
  return checksum;
}

for (let value = 0; value <= 255; value++) {
  if (barHeights[value] !== (value / 255) * canvasHeight) throw new Error('Bar height lookup differs');
}

function measure(frame, iterations) {
  let checksum = 0;
  const start = performance.now();
  for (let i = 0; i < iterations; i++) checksum += frame();
  return { ms: performance.now() - start, checksum };
}

const iterations = 1000000;
const rounds = 9;
const before = [];
const after = [];
for (let i = 0; i < 2; i++) {
  measure(baselineHeights, 2000);
  measure(lookupHeights, 2000);
}
for (let i = 0; i < rounds; i++) {
  before.push(measure(baselineHeights, iterations));
  after.push(measure(lookupHeights, iterations));
}
const median = values => values.sort((a, b) => a - b)[Math.floor(values.length / 2)];
const beforeMs = median(before.map(value => value.ms));
const afterMs = median(after.map(value => value.ms));
const baselineChecksum = baselineHeights();
const lookupChecksum = lookupHeights();
if (baselineChecksum !== lookupChecksum) throw new Error('Visualizer bar heights differ');
console.log(JSON.stringify({
  workload: `${iterations} visualizer frames/round, ${dataArray.length} bars/frame, median of ${rounds} rounds`,
  beforeMs: Number(beforeMs.toFixed(2)),
  afterMs: Number(afterMs.toFixed(2)),
  improvementPercent: Number(((beforeMs - afterMs) / beforeMs * 100).toFixed(1)),
  outputEquality: baselineChecksum === lookupChecksum
}));
