const dataArray = Uint8Array.from({ length: 128 }, (_, index) => (index * 37) % 256);
const canvas = { width: 320, height: 100 };

function createContext() {
  let fillStyle;
  let styleWrites = 0;
  let drawChecksum = 0;
  return {
    get styleWrites() { return styleWrites; },
    get drawChecksum() { return drawChecksum; },
    clearRect() {},
    fillRect(x, y, width, height) {
      drawChecksum += x + y + width + height;
    },
    set fillStyle(value) {
      fillStyle = value;
      styleWrites++;
    },
    get fillStyle() { return fillStyle; }
  };
}

function baselineFrame(ctx) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const barWidth = (canvas.width / dataArray.length) * 1.5;
  let x = 0;
  for (let i = 0; i < dataArray.length; i++) {
    const barHeight = (dataArray[i] / 255) * canvas.height;
    ctx.fillStyle = '#00f0ff';
    ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
    x += barWidth;
  }
}

function optimizedFrame(ctx) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const barWidth = (canvas.width / dataArray.length) * 1.5;
  let x = 0;
  ctx.fillStyle = '#00f0ff';
  for (let i = 0; i < dataArray.length; i++) {
    const barHeight = (dataArray[i] / 255) * canvas.height;
    ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
    x += barWidth;
  }
}

const baselineContext = createContext();
const optimizedContext = createContext();
baselineFrame(baselineContext);
optimizedFrame(optimizedContext);
if (baselineContext.drawChecksum !== optimizedContext.drawChecksum) throw new Error('visualizer drawing output mismatch');

function measure(frame, iterations) {
  const ctx = createContext();
  const start = process.hrtime.bigint();
  for (let i = 0; i < iterations; i++) frame(ctx);
  return { ms: Number(process.hrtime.bigint() - start) / 1e6, styleWrites: ctx.styleWrites, drawChecksum: ctx.drawChecksum };
}

const rounds = 7;
const iterations = 50000;
const baseline = [];
const optimized = [];
for (let i = 0; i < 2; i++) {
  measure(baselineFrame, 2000);
  measure(optimizedFrame, 2000);
}
for (let i = 0; i < rounds; i++) {
  baseline.push(measure(baselineFrame, iterations));
  optimized.push(measure(optimizedFrame, iterations));
}

const median = (values) => values.map((value) => value.ms).sort((a, b) => a - b)[Math.floor(values.length / 2)];
const baselineMs = median(baseline);
const optimizedMs = median(optimized);
const baselineStyleWrites = baseline[0].styleWrites / iterations;
const currentStyleWrites = optimized[0].styleWrites / iterations;
if (baseline.some((value) => value.drawChecksum !== optimized[0].drawChecksum) ||
    optimized.some((value) => value.drawChecksum !== baseline[0].drawChecksum)) {
  throw new Error('visualizer benchmark checksum mismatch');
}
console.log(JSON.stringify({
  workload: '128 bars per frame',
  framesPerRound: iterations,
  rounds,
  baselineMs: Number(baselineMs.toFixed(2)),
  optimizedMs: Number(optimizedMs.toFixed(2)),
  improvementPercent: Number(((baselineMs - optimizedMs) / baselineMs * 100).toFixed(1)),
  baselineStyleWrites,
  currentStyleWrites,
  outputEquality: true
}));
