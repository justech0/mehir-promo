"""Synthesises the 15 s soundtrack: darbuka groove (maqsum) at 100 BPM, sub bass,
Hijaz pluck motif, fire crackle, whooshes and hits locked to the video cuts.
Everything is generated here, so there are no licensing issues."""
import numpy as np, wave

SR = 44100
DUR = 15.0
N = int(SR * DUR)
BEAT = 0.6
rng = np.random.default_rng(72)
L = np.zeros(N); R = np.zeros(N)

def t_(d): return np.arange(int(SR * d)) / SR

def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    s = sig[: N - i] * gain
    L[i:i + len(s)] += s * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(s)] += s * np.sqrt(0.5 * (1 + pan))

def bandpass(x, lo, hi, taps=511):
    n = np.arange(taps) - taps // 2
    h = (2 * hi / SR) * np.sinc(2 * hi * n / SR) - (2 * lo / SR) * np.sinc(2 * lo * n / SR)
    h *= np.hamming(taps)
    return np.convolve(x, h, mode="same")

def lowpass(x, fc, taps=511):
    n = np.arange(taps) - taps // 2
    h = (2 * fc / SR) * np.sinc(2 * fc * n / SR) * np.hamming(taps)
    return np.convolve(x, h, mode="same")

# ---------- instruments ----------
def doum(g=1.0):
    t = t_(0.5)
    f = 52 + 90 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7)
    click = bandpass(rng.standard_normal(len(t)), 800, 3000) * np.exp(-t * 120) * .5
    return (body + click) * g

def tek(g=1.0, bright=1.0):
    t = t_(0.12)
    n = bandpass(rng.standard_normal(len(t)), 2500 * bright, 7000)
    ring = np.sin(2 * np.pi * 1850 * bright * t) * .35
    return (n * 1.4 + ring) * np.exp(-t * 55) * g

def shaker(g=1.0):
    t = t_(0.06)
    return bandpass(rng.standard_normal(len(t)), 6000, 12000) * np.exp(-t * 80) * g

def sub(freq, dur, g=1.0):
    t = t_(dur)
    env = np.minimum(1, t * 40) * np.exp(-t * 1.6)
    return (np.sin(2 * np.pi * freq * t) + .25 * np.sin(4 * np.pi * freq * t)) * env * g

def pluck(freq, dur=0.9, g=1.0):
    n = int(SR * dur); p = int(SR / freq)
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return lowpass(out, 4000, 255) * g

def boom(g=1.0):
    t = t_(1.6)
    f = 38 + 60 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    noise = lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t * 9) * .6
    return np.tanh((body + noise) * 1.6) * g

def whoosh(dur=0.5, g=1.0):
    n = rng.standard_normal(int(SR * dur)); t = t_(dur)
    out = np.zeros_like(n); seg = int(SR * 0.02)
    for k in range(0, len(n), seg):           # rising band sweep
        p = k / len(n); lo = 300 + 3500 * p ** 2
        out[k:k + seg] = bandpass(n[max(0, k - 600):k + seg + 600], lo, lo * 2.2, 255)[600 if k else 0:][:len(out[k:k + seg])]
    env = (t / dur) ** 2.2
    return out * env * g

def thud(g=1.0):
    t = t_(0.25)
    return (np.sin(2 * np.pi * (90 + 120 * np.exp(-t * 40)) * t) * np.exp(-t * 18) + lowpass(rng.standard_normal(len(t)), 1500, 255) * np.exp(-t * 40) * .4) * g

def click(g=1.0):
    t = t_(0.05)
    return (np.sin(2 * np.pi * 2400 * t) * .6 + bandpass(rng.standard_normal(len(t)), 3000, 9000, 255)) * np.exp(-t * 160) * g

def crackle(dur, g=1.0):
    n = int(SR * dur)
    bed = lowpass(rng.standard_normal(n), 700) * .35
    pops = np.zeros(n)
    for _ in range(int(dur * 45)):
        i = rng.integers(0, n - 800); a = rng.uniform(.2, 1)
        pops[i:i + 400] += rng.standard_normal(400) * np.exp(-np.arange(400) / rng.uniform(20, 90)) * a
    pops = bandpass(pops, 1500, 9000, 255)
    return (bed + pops * .5) * g

def fireburst(g=1.0):
    t = t_(1.4)
    n = lowpass(rng.standard_normal(len(t)), 2200)
    env = np.minimum(1, t * 12) * np.exp(-t * 2.2)
    return n * env * g

# ---------- arrangement ----------
CUTS = {"s2": 2.4, "s3": 5.4, "s4": 8.4, "s5": 11.4, "s6": 13.2}

# fire: big burst on frame 1, crackle under hook and end card
add(fireburst(.9), 0.0)
add(crackle(2.6, .5), 0.0)
add(crackle(2.0, .35), 13.2)

# hits on cuts
add(boom(1.0), 0.0)
for c, g in [(2.4, .8), (8.4, .9), (13.2, 1.0)]: add(boom(g), c)
for c in [2.4, 5.4, 8.4, 11.4, 13.2]: add(whoosh(.45, .35), c - .45, pan=0)

# hook: doum on each beat, building
for b in range(4):
    add(doum(.55 + b * .1), b * BEAT)
    if b >= 2: add(tek(.25), b * BEAT + .3, pan=.3)

# full maqsum groove from 2.4 to 13.2: D T . T D . T . (eighth notes)
pattern = ["D", "T", None, "T", "D", None, "T", None]
e = BEAT / 2
t0 = 2.4
k = 0
while t0 + k * e < 13.2 - 0.01:
    at = t0 + k * e
    s = pattern[k % 8]
    if s == "D": add(doum(.9), at)
    if s == "T": add(tek(.42, 1.0 if k % 2 else 1.15), at, pan=.25)
    if s is None: add(tek(.16, 1.3), at, pan=-.3)       # ghost "ka"
    add(shaker(.10 + .05 * (k % 2 == 0)), at, pan=-.4)
    add(shaker(.06), at + e / 2, pan=.4)
    k += 1

# sub bass: A1 with Hijaz move to Bb on bar 3
roots = [55.0, 55.0, 58.27, 55.0, 49.0]
for i, c in enumerate(np.arange(2.4, 13.2, 2.4)):
    add(sub(roots[i % len(roots)], 2.3, .55), c)
    add(sub(roots[i % len(roots)], 1.0, .35), c + 1.2)

# Hijaz pluck motif (A Bb C# D E F G), echoed
A = 220.0
H = {"A": A, "Bb": A * 2 ** (1/12), "C#": A * 2 ** (4/12), "D": A * 2 ** (5/12), "E": A * 2 ** (7/12), "F": A * 2 ** (8/12), "G": A * 2 ** (10/12), "A2": A * 2}
motif = [("A", 0), ("Bb", .3), ("C#", .6), ("D", .9), ("E", 1.5), ("D", 1.8), ("C#", 2.1)]
for start in [2.4, 4.8]:
    for n, o in motif: add(pluck(H[n], .9, .32), start + o, pan=-.2)
for start in [8.4, 10.8]:
    for n, o in [("E", 0), ("F", .3), ("E", .6), ("D", .9), ("C#", 1.2), ("D", 1.5), ("Bb", 1.8), ("A", 2.1)]:
        add(pluck(H[n] * (1 if start == 8.4 else 2), .9, .3), start + o, pan=.2)

# UI moments
add(click(.6), 7.2, pan=.1)
for i in range(3): add(thud(.75), 9.0 + i * .6, pan=(i - 1) * .3)

# ending: final hit, drone resolve on A, last doum
add(sub(55.0, 1.8, .7), 13.2)
for n, o in [("A2", 0), ("E", .15), ("C#", .3), ("A", .6)]: add(pluck(H[n], 1.4, .35), 13.25 + o)
add(doum(1.0), 14.4)
add(tek(.3), 14.7, pan=.3)

# ---------- master ----------
mix = np.stack([L, R])
# room: short convolution reverb
ir_t = t_(0.9); ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 6) * .025
ir[0] = 1.0
F = 1 << int(np.ceil(np.log2(N + len(ir))))
irf = np.fft.rfft(ir, F)
mix = np.stack([np.fft.irfft(np.fft.rfft(ch, F) * irf, F)[:N] for ch in mix])
# glue: soft clip + fade out last 0.5 s
mix = np.tanh(mix * 1.1)
fade = np.ones(N); fl = int(SR * .5); fade[-fl:] = np.linspace(1, 0, fl) ** 1.5
mix *= fade
mix /= np.max(np.abs(mix)) / 0.89
pcm = (mix.T * 32767).astype(np.int16)
with wave.open("soundtrack.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("soundtrack.wav", N / SR, "s")
