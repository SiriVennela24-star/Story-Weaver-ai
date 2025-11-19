"""
Simple audio renderer for StoryWeaver AI.
Produces short WAV files (synthesized) from track metadata.

This is intentionally lightweight and dependency-free (uses numpy and wave from stdlib).
"""
import io
import math
import wave
from typing import Dict, Any

import numpy as np


def _build_scale_frequencies(key: str = "C"):
    note_to_semitone = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    base = note_to_semitone.get((key or "C").upper()[0], 0)
    a4 = 440.0
    intervals = [0, 2, 4, 5, 7, 9, 11, 12]
    freqs = [a4 * (2 ** ((base + i) / 12.0)) for i in intervals]
    return freqs


def render_wav_bytes(track: Dict[str, Any], duration_seconds: int = 60, sample_rate: int = 44100) -> bytes:
    """Synthesize high-quality WAV audio from track metadata.

    Produces multi-layered music with melody, bass, and pads using different timbres.

    Args:
        track: dict with keys like 'title', 'tempo', 'key', 'genre', 'emotional_tone'
        duration_seconds: length of output in seconds
        sample_rate: audio sample rate

    Returns:
        bytes of WAV file
    """
    sr = sample_rate
    t = np.linspace(0, duration_seconds, int(sr * duration_seconds), endpoint=False)

    # Seed deterministic PRNG from track metadata
    seed_str = f"{track.get('title','')}-{track.get('genre','')}-{track.get('tempo',120)}"
    seed = abs(hash(seed_str)) % (2 ** 32)
    rng = np.random.RandomState(seed)

    scale = _build_scale_frequencies(track.get("key", "C"))
    bpm = max(60, int(track.get("tempo", 120)))
    beat = 60.0 / bpm
    genre = (track.get("genre", "ambient") or "ambient").lower()
    tone = (track.get("emotional_tone", "neutral") or "neutral").lower()

    signal = np.zeros_like(t)

    # ==== Bass layer (fundamental harmony) ====
    bass_signal = _render_bass_layer(scale, beat, sr, t, rng, duration_seconds)
    signal += bass_signal * 0.15

    # ==== Pad layer (atmospheric background) ====
    pad_signal = _render_pad_layer(scale, sr, t, rng, duration_seconds, genre)
    signal += pad_signal * 0.1

    # ==== Melody layer (main voice) ====
    melody_signal = _render_melody_layer(scale, beat, sr, t, rng, duration_seconds, genre, tone)
    signal += melody_signal * 0.5

    # ==== Accompaniment layer (chords/texture) ====
    accomp_signal = _render_accompaniment_layer(scale, beat, sr, t, rng, duration_seconds)
    signal += accomp_signal * 0.15

    # ==== Apply simple reverb effect ====
    signal = _apply_reverb(signal, sr)

    # Normalize and prevent clipping
    maxval = np.max(np.abs(signal))
    if maxval > 0:
        signal = signal / maxval * 0.85  # Leave some headroom

    # Convert to 16-bit PCM
    pcm = np.clip(signal * 32767.0, -32768, 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    return buf.getvalue()


def _render_bass_layer(scale, beat, sr, t, rng, duration_seconds):
    """Render slow-moving bass notes (root and fifth)."""
    signal = np.zeros_like(t)
    bass_scale = [f * 0.5 for f in scale[:3]]  # Lower octave
    
    # 2-note pattern: root and fifth
    pattern = [0, 1, 0, 1]
    beat_len = int(beat * sr * 2)  # 2-beat notes
    
    for i, note_idx in enumerate(pattern):
        start = i * beat_len
        if start >= len(t):
            break
        end = min(start + beat_len, len(t))
        if end <= start:
            continue
        
        freq = bass_scale[note_idx % len(bass_scale)]
        seg_t = t[start:end]
        # Smooth envelope with slow attack/release
        env = np.sin(np.linspace(0, np.pi, len(seg_t))) ** 0.7
        seg = 0.4 * np.sin(2 * np.pi * freq * (seg_t - seg_t[0])) * env
        signal[start:end] = seg
    
    # Loop the pattern
    remaining = len(t) - beat_len * len(pattern)
    if remaining > 0:
        signal[-remaining:] = signal[:remaining]
    
    return signal


def _render_pad_layer(scale, sr, t, rng, duration_seconds, genre):
    """Render ambient pad (slowly evolving chords)."""
    signal = np.zeros_like(t)
    
    # Chord: root, third, fifth
    chord_freqs = [scale[0], scale[2], scale[4]]
    
    # Slow waveform (8-second cycle)
    slow_cycle = int(8 * sr)
    slow_wave = np.sin(2 * np.pi * t / slow_cycle)
    
    for freq in chord_freqs:
        # Slight frequency modulation for richness
        mod_freq = freq * (1 + 0.02 * slow_wave)
        seg = np.sin(2 * np.pi * mod_freq * t)
        signal += seg
    
    signal /= len(chord_freqs)  # Average
    
    # Smooth envelope that fades in and out
    env = np.sin(np.linspace(0, np.pi, len(t))) ** 2
    signal *= env
    
    return signal * 0.3


def _render_melody_layer(scale, beat, sr, t, rng, duration_seconds, genre, tone):
    """Render the main melodic line."""
    signal = np.zeros_like(t)
    note_dur = beat if genre == "upbeat" else beat * 1.5
    notes_count = int(duration_seconds / note_dur)
    
    # Melodic contour depends on emotional tone
    if "dark" in tone or "sad" in tone:
        contour = [-3, -5, -2, -4, -2, 0, -1]  # Descending intervals
    elif "bright" in tone or "happy" in tone:
        contour = [0, 2, 4, 5, 4, 2, 0]  # Ascending/arching
    else:
        contour = [-1, 1, -2, 2, 0, 1, -1]  # Mixed
    
    for i in range(notes_count):
        start = int(i * note_dur * sr)
        if start >= len(t):
            break
        end = int(min((i + 1) * note_dur * sr, len(t)))
        if end <= start:
            continue
        
        # Pick note from scale using contour
        contour_idx = contour[i % len(contour)]
        scale_idx = (3 + contour_idx) % len(scale)  # Around middle of scale
        freq = scale[scale_idx]
        
        seg_t = t[start:end]
        # Slightly longer attack and release
        attack_len = int(0.05 * sr)
        release_len = int(0.1 * sr)
        total_len = len(seg_t)
        
        env = np.ones(total_len)
        if total_len > attack_len + release_len:
            env[:attack_len] = np.linspace(0, 1, attack_len)
            env[-release_len:] = np.linspace(1, 0, release_len)
        
        # Slight vibrato
        vibrato = 1 + 0.02 * np.sin(2 * np.pi * 5 * (seg_t - seg_t[0]))
        seg = 0.3 * np.sin(2 * np.pi * freq * vibrato * (seg_t - seg_t[0])) * env
        signal[start:end] = seg
    
    return signal


def _render_accompaniment_layer(scale, beat, sr, t, rng, duration_seconds):
    """Render supporting notes (arpeggios/texture)."""
    signal = np.zeros_like(t)
    arp_dur = beat * 0.5
    arp_count = int(duration_seconds / arp_dur)
    
    # 4-note arpeggio pattern
    arp_pattern = [0, 2, 4, 2]
    
    for i in range(arp_count):
        start = int(i * arp_dur * sr)
        if start >= len(t):
            break
        end = int(min((i + 1) * arp_dur * sr, len(t)))
        if end <= start:
            continue
        
        scale_idx = arp_pattern[i % len(arp_pattern)]
        freq = scale[scale_idx % len(scale)]
        
        seg_t = t[start:end]
        env = np.linspace(1, 0, len(seg_t))  # Quick decay
        seg = 0.15 * np.sin(2 * np.pi * freq * (seg_t - seg_t[0])) * env
        signal[start:end] += seg
    
    return signal


def _apply_reverb(signal, sr, delay_ms=150, decay=0.5):
    """Apply simple reverb effect using delayed copies."""
    delay_samples = int(delay_ms * sr / 1000.0)
    if delay_samples >= len(signal):
        return signal
    
    # Create delayed copy
    delayed = np.zeros_like(signal)
    delayed[delay_samples:] = signal[:-delay_samples] * decay
    
    # Mix with original
    return signal + delayed
