"""Original ambient score, synthesised from scratch with numpy (no samples, no downloads).

Slow pads, a soft bass and a sparse bell-like melody in D major / B minor, with reverb.
make_music(total_seconds, moods, path) writes a 44.1 kHz stereo WAV.
moods: list of (start_second, mood) with mood in {"day", "night", "rise", "home"}.
"""
import wave

import numpy as np

SR = 44100
CH = 8.0  # seconds per chord

#        bass  pad notes (midi)        chord tones for the melody
CHORDS = {
    "D":   (38, [54, 57, 62, 64], [62, 66, 69, 74]),
    "G":   (43, [55, 59, 62, 67], [62, 67, 71, 74]),
    "Bm":  (35, [54, 59, 62, 66], [59, 62, 66, 71]),
    "A":   (33, [52, 57, 61, 64], [64, 69, 73, 76]),
    "Em":  (40, [52, 55, 59, 64], [59, 64, 67, 71]),
    "F#m": (42, [54, 57, 61, 66], [61, 66, 69]),
}
PROG = {
    "day": ["D", "G", "Bm", "A", "D", "Bm", "G", "A"],
    "night": ["Bm", "G", "Em", "F#m"],
    "rise": ["G", "A", "Bm", "G", "A"],
    "home": ["D", "G", "D", "A"],
}
SCALE_HI = [62, 64, 66, 69, 71, 74, 76, 78, 81]   # D major pentatonic
SCALE_LO = [54, 57, 59, 62, 64, 66, 69, 71]       # same notes, lower (B minor colour)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(buf, t0, left, right):
    i = int(t0 * SR)
    if i < 0:
        left, right, i = left[-i:], right[-i:], 0
    n = min(len(left), buf.shape[0] - i)
    if n > 0:
        buf[i:i + n, 0] += left[:n]
        buf[i:i + n, 1] += right[:n]


def pad_note(m, dur, amp, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    att, rel = 3.0, 3.5
    env = np.minimum(1, t / att) ** 2 * np.minimum(1, (dur - t) / rel) ** 2
    env *= 1 + 0.06 * np.sin(2 * np.pi * 0.17 * t + rng.uniform(0, 6))
    out = []
    for cents in (-4, 4):
        f = hz(m) * 2 ** (cents / 1200)
        ph = rng.uniform(0, 6.28)
        s = (np.sin(2 * np.pi * f * t + ph) + 0.30 * np.sin(4 * np.pi * f * t + ph * 2)
             + 0.10 * np.sin(6 * np.pi * f * t) + 0.04 * np.sin(8 * np.pi * f * t))
        out.append(s * env * amp)
    return out[0] * 0.8 + out[1] * 0.2, out[0] * 0.2 + out[1] * 0.8


def bell_note(m, amp, pan):
    dur = 5.0
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.5)
         + 0.42 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.8)
         + 0.16 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.4)
         + 0.07 * np.sin(2 * np.pi * 4.2 * f * t) * np.exp(-t / 0.15))
    s *= np.minimum(1, t / 0.012) * np.minimum(1, (dur - t) / 0.5) * amp
    return s * (1 - pan), s * pan


def reverb(x, rng):
    n = int(3.6 * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    size = 1 << int(np.ceil(np.log2(x.shape[0] + n)))
    for ch in (0, 1):
        ir = rng.standard_normal(n) * np.exp(-t / 0.85)
        ir = np.convolve(ir, np.ones(10) / 10, mode="same")   # darker tail
        ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.fft.irfft(np.fft.rfft(x[:, ch], size) * np.fft.rfft(ir, size), size)
        out[:, ch] = wet[: x.shape[0]]
    return out


def mood_at(t, moods):
    cur = moods[0][1]
    for start, m in moods:
        if t >= start:
            cur = m
    return cur


def make_music(total, moods, path, seed=11):
    rng = np.random.default_rng(seed)
    buf = np.zeros((int(total * SR) + 1, 2))
    n_ch = int(np.ceil(total / CH))
    names, count = [], {}
    for i in range(n_ch):
        m = mood_at(i * CH + CH / 2, moods)
        k = count.get(m, 0)
        count[m] = k + 1
        names.append((m, PROG[m][k % len(PROG[m])]))
    names[-1] = ("home", "D")           # always come home at the end
    if n_ch > 1:
        names[-2] = ("home", "A")
    if n_ch > 2:
        names[-3] = ("home", "G")
    idx = 4
    for i, (mood, name) in enumerate(names):
        bass, pads, tones = CHORDS[name]
        t0 = i * CH
        soft = 0.8 if mood == "night" else 1.0
        for m in pads:
            l, r = pad_note(m, CH + 4.0, 0.050 * soft, rng)
            add(buf, t0 - 1.0, l, r)
        l, r = pad_note(bass, CH + 3.0, 0.085, rng)
        add(buf, t0 - 0.5, (l + r) / 2, (l + r) / 2)
        l, r = pad_note(bass + 12, CH + 3.0, 0.030, rng)
        add(buf, t0 - 0.5, l, r)
        # melody: a slow stepwise walk on the pentatonic scale, leaning on chord tones
        scale = SCALE_LO if mood == "night" else SCALE_HI
        prob = {"day": 0.50, "night": 0.30, "rise": 0.55, "home": 0.60}[mood]
        if t0 < 6 or t0 > total - 10:
            prob = 0.0 if t0 < 6 else 0.25
        idx = min(idx, len(scale) - 1)
        for beat in range(8):
            strong = beat in (0, 4)
            if rng.random() > (prob + 0.3 if strong else prob):
                continue
            idx = int(np.clip(idx + rng.choice([-2, -1, -1, 0, 1, 1, 2]), 0, len(scale) - 1))
            note = scale[idx]
            if strong:
                cands = [c + o for c in tones for o in (-12, 0, 12) if scale[0] <= c + o <= scale[-1]]
                note = min(cands, key=lambda c: abs(c - note))
                idx = int(np.argmin([abs(s - note) for s in scale]))
            amp = 0.13 * rng.uniform(0.55, 1.0) * (0.8 if mood == "night" else 1.0)
            l, r = bell_note(note, amp, rng.uniform(0.3, 0.7))
            add(buf, t0 + beat * 1.0 + rng.uniform(-0.02, 0.02), l, r)
    # final sustained D
    for m in (50, 57, 62, 66, 74):
        l, r = bell_note(m, 0.07, 0.5)
        add(buf, total - 9.0, l, r)
    buf = buf * 0.8 + reverb(buf, rng) * 0.55
    t = np.arange(buf.shape[0]) / SR
    buf *= (np.minimum(1, t / 3.0) * np.minimum(1, np.maximum(0, total - t) / 6.0))[:, None]
    buf *= 0.5 / np.max(np.abs(buf))
    pcm = (buf * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    rms = 20 * np.log10(np.sqrt(np.mean(buf ** 2)))
    return [n for _, n in names], rms
