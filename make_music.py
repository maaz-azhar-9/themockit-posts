"""Original 'time pressure' background track (no samples, fully synthesized).
~100 BPM: kick, clock ticks, pulsing minor bass, tension pad and a riser. Writes music.m4a.
"""
import os, subprocess, wave
import numpy as np

SR, DUR, BPM = 44100, 8.0, 100
ROOT = os.path.dirname(os.path.abspath(__file__))
t = np.arange(int(SR * DUR)) / SR
beat = 60 / BPM
mix = np.zeros_like(t)
rng = np.random.default_rng(7)


def place(sound, at, gain=1.0):
    i = int(at * SR)
    n = min(len(sound), len(mix) - i)
    if n > 0:
        mix[i:i + n] += gain * sound[:n]


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


# kick: pitch-dropping sine
kt = np.arange(int(0.35 * SR)) / SR
kick = np.sin(2 * np.pi * (45 * kt + 60 * (1 - np.exp(-kt * 30)) / 30)) * np.exp(-kt * 9)

# clock tick: short filtered noise burst + high blip
ct = np.arange(int(0.03 * SR)) / SR
tick_hi = (rng.standard_normal(len(ct)) * 0.4 + np.sin(2 * np.pi * 3200 * ct)) * np.exp(-ct * 260)
tick_lo = (rng.standard_normal(len(ct)) * 0.4 + np.sin(2 * np.pi * 2300 * ct)) * np.exp(-ct * 260)

n_beats = int(DUR / beat) + 1
for b in range(n_beats):
    place(kick, b * beat, 0.9)
    place(tick_hi if b % 2 == 0 else tick_lo, b * beat, 0.22)
    place(tick_lo, b * beat + beat / 2, 0.14)

# pulsing bass: A minor root / F, 16th-note gated saw, low-passed
notes = [55.0, 55.0, 43.65, 49.0]  # A1, A1, F1, G1 per bar
bar = 4 * beat
freq = np.array([notes[int(x // bar) % 4] for x in t])
phase = np.cumsum(freq) / SR
saw = 2 * (phase % 1) - 1
sixteenth = beat / 4
gate = np.exp(-((t % sixteenth) / sixteenth) * 4)
bass = lowpass(saw * gate, 380)
mix += 0.55 * bass / (np.abs(bass).max() + 1e-9)

# tension pad: detuned high fifth with slow tremolo
pad = (np.sin(2 * np.pi * 659.3 * t) + np.sin(2 * np.pi * 662 * t) + 0.6 * np.sin(2 * np.pi * 440 * t))
pad *= 0.5 + 0.5 * np.sin(2 * np.pi * (BPM / 60) * t)
mix += 0.05 * pad * np.minimum(t / 1.5, 1)

# riser in the last 3 seconds: rising tone + noise swell
rs = t >= DUR - 3
rt = t[rs] - (DUR - 3)
riser = np.sin(2 * np.pi * (300 * rt + 220 * rt ** 2)) * 0.5 + rng.standard_normal(rs.sum()) * 0.25
mix[rs] += 0.18 * riser * (rt / 3) ** 2

# master: fade in/out, normalize
mix *= np.minimum(t / 0.05, 1) * np.minimum((DUR - t) / 0.6, 1)
mix = np.tanh(mix * 1.3)
mix = mix / np.abs(mix).max() * 0.89
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)

wav = os.path.join(ROOT, "music.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "aac", "-b:a", "160k",
                os.path.join(ROOT, "music.m4a")], check=True)
os.remove(wav)
print("music.m4a")
