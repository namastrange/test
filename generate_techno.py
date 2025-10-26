#!/usr/bin/env python3
"""
UK Garage / Broken Beat Track Generator
Generates a swung, percussive track with organic instruments inspired by Bliss Inc, Adam Pits
"""

import numpy as np
import soundfile as sf
from scipy import signal

# Audio parameters
SAMPLE_RATE = 44100
BPM = 128
DURATION = 120  # 2 minutes
SWING_AMOUNT = 0.15  # 15% swing (delays every other 16th note)

# Calculate timing
beat_duration = 60.0 / BPM
bar_duration = beat_duration * 4
sixteenth_duration = beat_duration / 4

def apply_swing(position, swing=SWING_AMOUNT):
    """Apply swing to timing positions (0-based 16th note position)"""
    if position % 2 == 1:  # Delay odd 16th notes
        return swing * sixteenth_duration
    return 0

def generate_sine(freq, duration, sample_rate=SAMPLE_RATE):
    """Generate a sine wave"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * freq * t)

def generate_saw(freq, duration, sample_rate=SAMPLE_RATE):
    """Generate a sawtooth wave"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return signal.sawtooth(2 * np.pi * freq * t)

def apply_adsr(audio, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
    """Apply ADSR envelope to audio"""
    length = len(audio)
    envelope = np.ones(length)

    attack_samples = min(int(attack * SAMPLE_RATE), length // 4)
    decay_samples = min(int(decay * SAMPLE_RATE), length // 4)
    release_samples = min(int(release * SAMPLE_RATE), length // 4)

    total_envelope_samples = attack_samples + decay_samples + release_samples
    if total_envelope_samples > length:
        scale = length / total_envelope_samples
        attack_samples = int(attack_samples * scale)
        decay_samples = int(decay_samples * scale)
        release_samples = int(release_samples * scale)

    sustain_samples = length - attack_samples - decay_samples - release_samples

    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    if decay_samples > 0:
        decay_end = attack_samples + decay_samples
        envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)

    if sustain_samples > 0:
        sustain_start = attack_samples + decay_samples
        sustain_end = sustain_start + sustain_samples
        envelope[sustain_start:sustain_end] = sustain

    if release_samples > 0:
        envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)

    return audio * envelope

def generate_kick(duration=0.5, pitch_variance=0):
    """Generate a garage-style kick drum with optional pitch variance"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Pitch envelope (add variance for humanization)
    base_pitch = 45 + pitch_variance
    pitch_env = base_pitch + 95 * np.exp(-t * 18)
    phase = np.cumsum(2 * np.pi * pitch_env / SAMPLE_RATE)
    kick = np.sin(phase)

    # Amplitude envelope (snappier for garage)
    amp_env = np.exp(-t * 10)
    kick = kick * amp_env

    # Add punch
    click = np.exp(-t * 120) * 0.35
    kick = kick + click

    return kick * 0.75

def generate_snare(duration=0.15):
    """Generate garage/broken beat snare"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Tone component (pitched element)
    tone_freq = 180 + 200 * np.exp(-t * 30)
    phase = np.cumsum(2 * np.pi * tone_freq / SAMPLE_RATE)
    tone = np.sin(phase) * 0.4

    # Noise component
    noise = np.random.randn(len(t))

    # Band-pass filter for snare brightness
    sos = signal.butter(2, [1000, 8000], 'bp', fs=SAMPLE_RATE, output='sos')
    noise = signal.sosfilt(sos, noise)

    snare = tone + noise * 0.6

    # Envelope
    env = np.exp(-t * 25)
    snare = snare * env

    return snare * 0.35

def generate_hihat(duration=0.08, closed=True, accent=False):
    """Generate hi-hat with variation"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Metallic noise
    noise = np.random.randn(len(t))

    # High-pass filter (different cutoff for variation)
    cutoff = 8000 if closed else 6000
    sos = signal.butter(4, cutoff, 'hp', fs=SAMPLE_RATE, output='sos')
    hihat = signal.sosfilt(sos, noise)

    # Envelope
    if closed:
        env = np.exp(-t * 60)
    else:
        env = np.exp(-t * 15)

    hihat = hihat * env

    # Accent
    volume = 0.18 if accent else 0.12
    return hihat * volume

def generate_tabla_ge(pitch=200, duration=0.3):
    """Generate tabla 'ge' sound (bass stroke)"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Pitched component with pitch bend
    pitch_env = pitch * (1 + 0.3 * np.exp(-t * 20))
    phase = np.cumsum(2 * np.pi * pitch_env / SAMPLE_RATE)
    tone = np.sin(phase)

    # Add harmonics
    tone += 0.3 * np.sin(2 * phase)
    tone += 0.15 * np.sin(3 * phase)

    # Membrane resonance
    resonance = signal.butter(2, [pitch * 1.2, pitch * 2.0], 'bp', fs=SAMPLE_RATE, output='sos')
    resonant = signal.sosfilt(resonance, np.random.randn(len(t)))

    tabla = tone * 0.7 + resonant * 0.3

    # Envelope
    env = np.exp(-t * 12)
    tabla = tabla * env

    return tabla * 0.3

def generate_tabla_na(duration=0.15):
    """Generate tabla 'na' sound (treble stroke)"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Higher pitched with more harmonics
    pitch = 450
    phase = 2 * np.pi * pitch * t
    tone = np.sin(phase) * 0.5
    tone += np.sin(2 * phase) * 0.3
    tone += np.sin(3 * phase) * 0.2

    # Add metallic noise
    noise = np.random.randn(len(t))
    sos = signal.butter(2, [1000, 5000], 'bp', fs=SAMPLE_RATE, output='sos')
    noise = signal.sosfilt(sos, noise)

    tabla = tone + noise * 0.4

    # Sharp envelope
    env = np.exp(-t * 35)
    tabla = tabla * env

    return tabla * 0.25

def generate_rim(duration=0.05):
    """Generate rim shot / stick sound"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # High frequency click
    noise = np.random.randn(len(t))
    sos = signal.butter(3, [2000, 10000], 'bp', fs=SAMPLE_RATE, output='sos')
    rim = signal.sosfilt(sos, noise)

    # Very sharp envelope
    env = np.exp(-t * 80)
    rim = rim * env

    return rim * 0.15

def generate_shaker(duration=0.06):
    """Generate shaker sound"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    noise = np.random.randn(len(t))

    # High-pass for brightness
    sos = signal.butter(2, 5000, 'hp', fs=SAMPLE_RATE, output='sos')
    shaker = signal.sosfilt(sos, noise)

    # Envelope
    env = np.exp(-t * 40)
    shaker = shaker * env

    return shaker * 0.08

def generate_bass_note(freq, duration):
    """Generate bass synth note"""
    sine = generate_sine(freq, duration)
    saw = generate_saw(freq, duration)
    bass = 0.6 * sine + 0.4 * saw

    # Low-pass filter
    sos = signal.butter(4, 320, 'lp', fs=SAMPLE_RATE, output='sos')
    bass = signal.sosfilt(sos, bass)

    # Apply envelope
    bass = apply_adsr(bass, attack=0.01, decay=0.15, sustain=0.55, release=0.25)

    return bass * 0.35

def generate_pad(freqs, duration):
    """Generate atmospheric pad"""
    pad = np.zeros(int(SAMPLE_RATE * duration))

    for freq in freqs:
        sine1 = generate_sine(freq, duration)
        sine2 = generate_sine(freq * 1.005, duration)
        sine3 = generate_sine(freq * 0.995, duration)
        layer = (sine1 + sine2 + sine3) / 3
        pad += layer

    pad = pad / len(freqs)
    pad = apply_adsr(pad, attack=1.0, decay=0.5, sustain=0.7, release=2.0)

    sos = signal.butter(2, 2200, 'lp', fs=SAMPLE_RATE, output='sos')
    pad = signal.sosfilt(sos, pad)

    return pad * 0.13

def add_to_track(track, audio, start_time):
    """Add audio to track at specified time"""
    start_sample = int(start_time * SAMPLE_RATE)
    end_sample = start_sample + len(audio)

    if end_sample > len(track):
        audio = audio[:len(track) - start_sample]
        end_sample = len(track)

    if start_sample < len(track):
        track[start_sample:end_sample] += audio

print("Generating UK Garage / Broken Beat track with swing and organic percussion...")
print(f"BPM: {BPM}, Swing: {SWING_AMOUNT*100}%, Duration: {DURATION}s")

# Initialize track
track = np.zeros(int(SAMPLE_RATE * DURATION))

# Bass line pattern - syncopated garage style
bass_notes = [110, 110, 165, 146.83, 110, 165, 130.81, 146.83]  # A, E, D, E, C#, D

# Pad progression
pad_progressions = [
    [220, 264, 330],         # A minor
    [174.61, 220, 261.63],   # F major
    [196, 246.94, 293.66],   # G major
    [164.81, 196, 246.94]    # E minor
]

total_bars = int(DURATION / bar_duration)

# Broken beat / 2-step patterns
def get_kick_pattern(bar):
    """Get syncopated kick pattern for this bar"""
    # Varies every 2 bars
    if bar % 4 < 2:
        return [0, 4, 6, 10, 14]  # 16th note positions
    else:
        return [0, 5, 8, 12, 15]

def get_snare_pattern(bar):
    """Get snare pattern"""
    if bar % 2 == 0:
        return [4, 12]  # Classic positions
    else:
        return [4, 10, 12]  # Syncopated

print("Building complex drum patterns with swing...")
for bar in range(total_bars):
    bar_start = bar * bar_duration

    # Syncopated kicks
    if bar >= 0:  # Kicks throughout
        kick_positions = get_kick_pattern(bar)
        for pos in kick_positions:
            kick_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
            variance = np.random.uniform(-2, 2) if bar % 8 >= 4 else 0
            kick = generate_kick(pitch_variance=variance)
            add_to_track(track, kick, kick_time)

    # Snares
    if bar >= 8:
        snare_positions = get_snare_pattern(bar)
        for pos in snare_positions:
            snare_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
            snare = generate_snare()
            add_to_track(track, snare, snare_time)

    # Complex hi-hat pattern with swing
    if bar >= 4:
        for pos in range(16):
            # Skip some for groove
            if pos % 4 == 1 and bar % 2 == 1:
                continue

            hihat_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
            is_closed = pos % 2 == 0 or pos % 4 == 3
            is_accent = pos % 4 == 0
            hihat = generate_hihat(closed=is_closed, accent=is_accent)
            add_to_track(track, hihat, hihat_time)

print("Adding tabla and organic percussion...")
# Tabla patterns
for bar in range(12, total_bars):
    bar_start = bar * bar_duration

    # Tabla ge (bass)
    if bar % 2 == 0:
        tabla_pattern = [2, 10]
    else:
        tabla_pattern = [1, 6, 13]

    for pos in tabla_pattern:
        tabla_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
        pitch = 200 + np.random.uniform(-10, 10)
        tabla = generate_tabla_ge(pitch=pitch)
        add_to_track(track, tabla, tabla_time)

    # Tabla na (treble) - every other bar
    if bar % 2 == 1 and bar >= 16:
        for pos in [7, 15]:
            tabla_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
            tabla = generate_tabla_na()
            add_to_track(track, tabla, tabla_time)

# Rim shots and percussion fills
print("Adding rim shots and shakers...")
for bar in range(20, total_bars):
    bar_start = bar * bar_duration

    # Rim shots on upbeats
    if bar % 4 == 3:
        for pos in [9, 11, 13]:
            rim_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
            rim = generate_rim()
            add_to_track(track, rim, rim_time)

    # Shakers for texture
    if bar >= 24:
        for pos in range(1, 16, 2):  # Odd 16ths
            if np.random.random() > 0.3:  # Randomize for organic feel
                shaker_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
                shaker = generate_shaker()
                add_to_track(track, shaker, shaker_time)

print("Adding syncopated bass line...")
for bar in range(16, total_bars):
    bar_start = bar * bar_duration

    # Syncopated bass positions
    if bar % 2 == 0:
        bass_positions = [(0, 0), (6, 1), (10, 2), (14, 3)]
    else:
        bass_positions = [(0, 4), (5, 5), (8, 6), (12, 7)]

    for pos, note_idx in bass_positions:
        bass_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
        bass = generate_bass_note(bass_notes[note_idx], sixteenth_duration * 3.5)
        add_to_track(track, bass, bass_time)

print("Adding atmospheric pads...")
for bar in range(32, total_bars):
    if bar % 8 == 0:
        pad_idx = ((bar - 32) // 8) % len(pad_progressions)
        pad = generate_pad(pad_progressions[pad_idx], bar_duration * 8)
        add_to_track(track, pad, bar * bar_duration)

print("Applying final processing...")
# Normalize
track = track / np.max(np.abs(track)) * 0.88

# Fade out
fadeout_start = int((DURATION - bar_duration * 8) * SAMPLE_RATE)
fadeout_length = len(track) - fadeout_start
fade_curve = np.linspace(1, 0, fadeout_length)
track[fadeout_start:] *= fade_curve

# Fade in
fadein_length = int(bar_duration * 2 * SAMPLE_RATE)
fade_in_curve = np.linspace(0, 1, fadein_length)
track[:fadein_length] *= fade_in_curve

# Convert to 16-bit
track = (track * 32767).astype(np.int16)

# Save
output_file = "minimal_techno_track.wav"
sf.write(output_file, track, SAMPLE_RATE)

print(f"\n✓ Track generated successfully!")
print(f"✓ Saved to: {output_file}")
print(f"✓ Style: UK Garage / Broken Beat with organic percussion")
print(f"✓ Duration: {DURATION}s ({total_bars} bars)")
print(f"✓ Features: Swung drums, tablas, complex syncopation")
print(f"✓ Format: 16-bit WAV, {SAMPLE_RATE}Hz")
