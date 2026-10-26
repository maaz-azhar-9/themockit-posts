"""Original calm 'thinking' background track (no samples, fully synthesized).
~80 BPM lo-fi feel: warm pad chords, soft plucked arpeggio, gentle tick, soft sub bass.
Writes music.m4a (8 s).
"""
import os, subprocess, wave
import numpy as np

SR, DUR, BPM = 44100, 8.0, 80
ROOT = os.path.dirname(os.path.abspath(__file__))
t = np.arange(int(SR * DUR)) / SR
beat = 60 / BPM
mix = np.zeros_like(t)
rng = np.random.default_rng(3)


def hz(m):  # midi -> Hz
    return 440 * 2 ** ((m - 69) / 12)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def place(buf, sound, at, gain=1.0):
    i = int(at * SR)
    n = min(len(sound), len(buf) - i)
    if n > 0:
        buf[i:i + n] += gain * sound[:n]


# chord progression, 2 beats each (1.5 s): Am7 - Fmaj7 - Cmaj7 - G6 (repeats)
chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 64]]
roots = [45, 41, 48, 43]
step = 2 * beat

# warm pad: soft triangle-ish (sine + 3rd harmonic), slow attack/release per chord
pad = np.zeros_like(t)
for k in range(int(DUR / step) + 1):
    c = chords[k % 4]
    seg = np.arange(int((step + 0.6) * SR)) / SR
    env = np.minimum(seg / 0.5, 1) * np.clip((step + 0.6 - seg) / 0.6, 0, 1)
    tone = sum(np.sin(2 * np.pi * hz(m) * seg) + 0.12 * np.sin(2 * np.pi * 3 * hz(m) * seg) for m in c)
    place(pad, tone * env, k * step, 0.25)
pad = lowpass(pad, 1400)
mix += 0.32 * pad / np.abs(pad).max()

# soft pluck arpeggio on 8th notes (upper chord tones)
pluck = np.zeros_like(t)
pt = np.arange(int(0.9 * SR)) / SR
for e in range(int(DUR / (beat / 2))):
    c = chords[int(e * (beat / 2) // step) % 4]
    m = (c + [c[1] + 12])[[0, 2, 1, 3, 4, 2, 3, 1][e % 8]] + 12
    note = (np.sin(2 * np.pi * hz(m) * pt) + 0.3 * np.sin(2 * np.pi * 2 * hz(m) * pt)) * np.exp(-pt * 5)
    place(pluck, note, e * beat / 2, 0.8 if e % 2 == 0 else 0.55)
pluck = lowpass(pluck, 2600)
mix += 0.22 * pluck / np.abs(pluck).max()

# soft sub bass, one note per chord
bass = np.zeros_like(t)
for k in range(int(DUR / step) + 1):
    seg = np.arange(int(step * SR)) / SR
    env = np.minimum(seg / 0.05, 1) * np.exp(-seg * 1.2)
    place(bass, np.sin(2 * np.pi * hz(roots[k % 4]) * seg) * env, k * step)
mix += 0.30 * bass / np.abs(bass).max()

# gentle clock tick on each beat (quiet, rounded), soft brush on off-beats
ct = np.arange(int(0.04 * SR)) / SR
tick = np.sin(2 * np.pi * 1800 * ct) * np.exp(-ct * 140)
brush = lowpass(rng.standard_normal(int(0.08 * SR)), 5000) * np.exp(-np.arange(int(0.08 * SR)) / SR * 45)
for b in range(int(DUR / beat) + 1):
    place(mix, tick, b * beat, 0.07)
    place(mix, brush, b * beat + beat / 2, 0.05)

# master: gentle fades, soft limiting, overall warmth
mix *= np.minimum(t / 0.8, 1) * np.minimum((DUR - t) / 1.2, 1)
mix = lowpass(mix, 7000)
mix = np.tanh(mix * 0.9)
mix = mix / np.abs(mix).max() * 0.8
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)

wav = os.path.join(ROOT, "music.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "aac", "-b:a", "160k",
                os.path.join(ROOT, "music.m4a")], check=True)
os.remove(wav)
print("music.m4a")
