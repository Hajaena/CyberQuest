"""Génération procédurale des sons 8-bit (ondes carrées), sans dépendance externe."""
import random
import struct
import wave

RATE = 22050


def _square(freq, dur, vol=0.3, duty=0.5):
    n = int(RATE * dur)
    if freq <= 0:
        return [0.0] * n
    period = RATE / freq
    out = []
    for i in range(n):
        phase = (i % period) / period
        env = min(1.0, i / (RATE * 0.004)) * (1.0 - i / n) ** 0.6
        out.append((vol if phase < duty else -vol) * env)
    return out


def _sweep(f0, f1, dur, vol=0.3):
    n = int(RATE * dur)
    phase = 0.0
    out = []
    for i in range(n):
        phase = (phase + (f0 + (f1 - f0) * i / n) / RATE) % 1.0
        out.append((vol if phase < 0.5 else -vol) * (1.0 - i / n))
    return out


def _noise(dur, vol=0.05, seed=1):
    rng = random.Random(seed)
    n = int(RATE * dur)
    return [rng.uniform(-vol, vol) * (1.0 - i / n) for i in range(n)]


def _mix(*tracks):
    out = [0.0] * max(len(t) for t in tracks)
    for track in tracks:
        for i, v in enumerate(track):
            out[i] += v
    return out


def _seq(notes, dur, vol=0.3):
    out = []
    for f in notes:
        out += _square(f, dur, vol)
    return out


def _write(path, samples):
    frames = b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples
    )
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(frames)


def _music():
    """Petite boucle chiptune : arpège en la mineur + basse + charleston."""
    chords = [
        (110.00, (220.00, 261.63, 329.63)),   # Am
        (87.31, (174.61, 220.00, 261.63)),    # F
        (130.81, (261.63, 329.63, 392.00)),   # C
        (98.00, (196.00, 246.94, 293.66)),    # G
    ]
    pattern = (0, 1, 2, 1, 0, 1, 2, 2)
    step = 0.15
    lead, bass, hat = [], [], []
    for rep in range(2):
        pat = pattern if rep == 0 else tuple(reversed(pattern))
        for root, notes in chords:
            for k in pat:
                lead += _square(notes[k] * 2, step, 0.10, 0.25)
            for j in range(4):
                bass += _square(root * (1 if j % 2 == 0 else 2), step * 2, 0.16, 0.5)
            for s in range(8):
                chunk = _noise(0.03, 0.05, seed=s + 1) if s % 2 else []
                hat += chunk + [0.0] * (int(RATE * step) - len(chunk))
    return _mix(lead, bass, hat)


SOUND_BUILDERS = {
    "click": lambda: _square(1200, 0.03, 0.25),
    "success": lambda: _seq([659.25, 783.99, 1046.50], 0.08),
    "error": lambda: _sweep(240, 80, 0.40, 0.35),
    "levelup": lambda: _seq([523.25, 659.25, 783.99, 1046.50, 1318.51], 0.10),
    "gameover": lambda: _seq([392.00, 370.00, 349.23, 329.63], 0.22)
    + _sweep(330, 50, 0.7, 0.3),
    "music": _music,
}


def ensure_sounds(directory, force=False):
    """Crée les fichiers .wav manquants dans `directory`."""
    directory.mkdir(parents=True, exist_ok=True)
    for name, build in SOUND_BUILDERS.items():
        path = directory / f"{name}.wav"
        if force or not path.exists():
            _write(path, build())
