// Renders scenes.html frame by frame (window.renderAt is deterministic) and
// encodes a 1080x1920 30fps MP4. `node render.js preview` = key-frame sheet only.
const http = require("http"), fs = require("fs"), path = require("path");
const { spawnSync } = require("child_process");
const puppeteer = require("puppeteer-core");
const ffmpeg = require("ffmpeg-static");

const ROOT = __dirname, FPS = 30, PORT = 5193;
const OUT = path.join(ROOT, "frames");
const TYPES = { ".svg": "image/svg+xml", ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".png": "image/png", ".jpg": "image/jpeg" };

const server = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split("?")[0]);
  if (p === "/") p = "/scenes.html";
  fs.readFile(path.join(ROOT, p), (e, b) => {
    if (e) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { "content-type": TYPES[path.extname(p)] || "application/octet-stream" });
    r.end(b);
  });
}).listen(PORT);

(async () => {
  const mode = process.argv[2] || "full";
  const browser = await puppeteer.launch({
    executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
    headless: "new", args: ["--force-color-profile=srgb", "--lang=tr-TR", "--enable-gpu-rasterization"],
  });
  const page = await browser.newPage();
  page.on("console", m => { if (m.type() === "error") console.log("PAGE:", m.text()); });
  page.on("pageerror", e => console.log("PAGEERR:", e.message));
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  await page.goto(`http://localhost:${PORT}/scenes.html`, { waitUntil: "networkidle0", timeout: 120000 });
  await page.waitForFunction("window.READY === true", { timeout: 120000 });
  const DUR = await page.evaluate(() => window.VIDEO_DURATION);

  if (mode === "preview" || mode === "at") {
    const times = mode === "at" ? process.argv.slice(3).map(Number)
      : [0.15, 0.4, 1.5, 3.0, 4.2, 5.8, 7.0, 7.9, 8.7, 9.6, 10.9, 11.8, 12.8, 13.4, 14.0, 14.9];
    const dir = path.join(ROOT, "preview"); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir);
    const list = [];
    for (const t of times) {
      await page.evaluate(tt => window.renderAt(tt), t);
      const f = path.join(dir, `p_${String(t).replace(".", "_")}.jpg`);
      await page.screenshot({ path: f, type: "jpeg", quality: 85 }); list.push(f);
    }
    const cols = Math.min(8, list.length);
    spawnSync(ffmpeg, ["-y", "-loglevel", "error", ...list.flatMap(f => ["-i", f]), "-filter_complex",
      `${list.map((_, i) => `[${i}:v]scale=270:480[s${i}]`).join(";")};${list.map((_, i) => `[s${i}]`).join("")}xstack=inputs=${list.length}:layout=${list.map((_, i) => `${(i % cols) * 270}_${Math.floor(i / cols) * 480}`).join("|")}:fill=black`,
      "-frames:v", "1", path.join(dir, "sheet.jpg")], { stdio: "inherit" });
    await browser.close(); server.close(); console.log("preview ready"); return;
  }

  fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT);
  const total = Math.round(DUR * FPS);
  for (let i = 0; i < total; i++) {
    await page.evaluate(tt => window.renderAt(tt), i / FPS);
    await page.screenshot({ path: path.join(OUT, `f${String(i).padStart(4, "0")}.jpg`), type: "jpeg", quality: 95 });
    if (i % 60 === 0) console.log(`${i}/${total}`);
  }
  await browser.close(); server.close();
  const mp4 = path.join(ROOT, "..", "mehir-siparis-reels-sessiz.mp4");
  spawnSync(ffmpeg, ["-y", "-loglevel", "error", "-framerate", String(FPS), "-i", path.join(OUT, "f%04d.jpg"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "17", "-preset", "slow",
    "-movflags", "+faststart", mp4], { stdio: "inherit" });
  console.log("done:", mp4);
})().catch(e => { console.error(e); process.exit(1); });
