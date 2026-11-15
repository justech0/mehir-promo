"""Cuts the ElevenLabs read into phrases and places each one on its moment in the video."""
import subprocess, sys

import os
FF = os.path.abspath(os.path.join(os.path.dirname(__file__), "node_modules", "ffmpeg-static", "ffmpeg.exe"))
SRC = sys.argv[1]
TEMPO = 1.06
PRE, POST = 0.04, 0.10

# (speech start, speech end) in the source file -> start time in the video
PHRASES = [
    ("Mehir",                   0.000,  0.586, 0.10),
    ("artık kapında",           1.019,  1.966, 0.80),
    ("Közün en lezzetli hali",  2.400,  4.145, 2.50),
    ("Şimdi",                   4.542,  5.008, 4.85),
    ("sadece bir tık uzağında", 5.322,  6.954, 5.42),
    ("Yemeksepeti'nde",         7.315,  8.343, 7.85),   # Yemeksepeti face lands 7.95
    ("Trendyol Go'da",          8.557,  9.589, 9.00),   # flip 8.75
    ("Migros Yemek'te",         9.817, 10.822, 10.10),  # flip 9.85
    ("ve Getir'de",            11.027, 11.812, 11.20),  # flip 10.95
    ("Köz bizden",             12.187, 13.023, 12.25),  # cut 12.15
    ("sofra senden",           13.253, 14.130, 13.12),
    ("Mehir Ocakbaşı",         14.483, 15.448, 14.04),
]

parts, labels = [], []
for i, (name, s, e, at) in enumerate(PHRASES):
    a, b = max(0, s - PRE), e + POST
    at_ms = max(0, int((at - PRE / TEMPO) * 1000))
    parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={TEMPO},"
                 f"afade=t=in:d=0.02,afade=t=out:st={(b - a) / TEMPO - 0.06:.3f}:d=0.06,adelay={at_ms}|{at_ms}[p{i}]")
    labels.append(f"[p{i}]")
    end = at + (e - s) / TEMPO
    print(f"{at:6.2f} - {end:5.2f}  {name}")

graph = ";".join(parts) + ";" + "".join(labels) + \
    f"amix=inputs={len(labels)}:normalize=0,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120," \
    "apad,atrim=0:15,loudnorm=I=-14:TP=-1.5:LRA=7,aformat=sample_rates=48000:channel_layouts=stereo[out]"
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", SRC, "-filter_complex", graph,
                "-map", "[out]", "voice_track.wav"], check=True)
print("voice_track.wav ok")
