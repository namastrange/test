#!/usr/bin/env python3
"""
Minimal Progressive Techno Track Generator
Generates a minimal prog techno track with synths and outputs to WAV file
"""

import numpy as np
import soundfile as sf
from scipy import signal

# Audio parameters
SAMPLE_RATE = 44100
BPM = 128
DURATION = 120  # 2 minutes

# Calculate timing
beat_duration = 60.0 / BPM
bar_duration = beat_duration * 4

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

    # Ensure we don't exceed total length
    total_envelope_samples = attack_samples + decay_samples + release_samples
    if total_envelope_samples > length:
        # Scale down proportionally
        scale = length / total_envelope_samples
        attack_samples = int(attack_samples * scale)
        decay_samples = int(decay_samples * scale)
        release_samples = int(release_samples * scale)

    sustain_samples = length - attack_samples - decay_samples - release_samples

    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay
    if decay_samples > 0:
        decay_end = attack_samples + decay_samples
        envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)

    # Sustain
    if sustain_samples > 0:
        sustain_start = attack_samples + decay_samples
        sustain_end = sustain_start + sustain_samples
        envelope[sustain_start:sustain_end] = sustain

    # Release
    if release_samples > 0:
        envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)

    return audio * envelope

def generate_kick(duration=0.5):
    """Generate a techno kick drum"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Pitch envelope for kick (starts at 150Hz, drops to 40Hz)
    pitch_env = 40 + 110 * np.exp(-t * 20)
    phase = np.cumsum(2 * np.pi * pitch_env / SAMPLE_RATE)
    kick = np.sin(phase)

    # Amplitude envelope
    amp_env = np.exp(-t * 8)
    kick = kick * amp_env

    # Add click
    click = np.exp(-t * 100) * 0.3
    kick = kick + click

    return kick * 0.8

def generate_hihat(duration=0.1, closed=True):
    """Generate hi-hat sound"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Noise
    noise = np.random.randn(len(t))

    # High-pass filter
    sos = signal.butter(4, 7000, 'hp', fs=SAMPLE_RATE, output='sos')
    hihat = signal.sosfilt(sos, noise)

    # Envelope
    if closed:
        env = np.exp(-t * 50)
    else:
        env = np.exp(-t * 10)

    return hihat * env * 0.15

def generate_bass_note(freq, duration):
    """Generate a bass synth note"""
    # Mix of sine and saw for thickness
    sine = generate_sine(freq, duration)
    saw = generate_saw(freq, duration)
    bass = 0.6 * sine + 0.4 * saw

    # Low-pass filter
    sos = signal.butter(4, 300, 'lp', fs=SAMPLE_RATE, output='sos')
    bass = signal.sosfilt(sos, bass)

    # Apply envelope
    bass = apply_adsr(bass, attack=0.01, decay=0.1, sustain=0.6, release=0.2)

    return bass * 0.4

def generate_pad(freqs, duration):
    """Generate atmospheric pad"""
    pad = np.zeros(int(SAMPLE_RATE * duration))

    for freq in freqs:
        # Layer multiple sine waves with slight detuning
        sine1 = generate_sine(freq, duration)
        sine2 = generate_sine(freq * 1.005, duration)
        sine3 = generate_sine(freq * 0.995, duration)

        layer = (sine1 + sine2 + sine3) / 3
        pad += layer

    pad = pad / len(freqs)

    # Slow attack/release for pad
    pad = apply_adsr(pad, attack=1.0, decay=0.5, sustain=0.7, release=2.0)

    # Low-pass filter for warmth
    sos = signal.butter(2, 2000, 'lp', fs=SAMPLE_RATE, output='sos')
    pad = signal.sosfilt(sos, pad)

    return pad * 0.15

def generate_arp_note(freq, duration):
    """Generate a short arpeggio note"""
    note = generate_saw(freq, duration)

    # Band-pass filter for presence
    sos = signal.butter(2, [800, 3000], 'bp', fs=SAMPLE_RATE, output='sos')
    note = signal.sosfilt(sos, note)

    # Short envelope
    note = apply_adsr(note, attack=0.005, decay=0.1, sustain=0.3, release=0.1)

    return note * 0.2

def add_to_track(track, audio, start_time):
    """Add audio to track at specified time"""
    start_sample = int(start_time * SAMPLE_RATE)
    end_sample = start_sample + len(audio)

    if end_sample > len(track):
        audio = audio[:len(track) - start_sample]
        end_sample = len(track)

    track[start_sample:end_sample] += audio

print("Generating minimal progressive techno track...")
print(f"BPM: {BPM}, Duration: {DURATION}s, Sample Rate: {SAMPLE_RATE}Hz")

# Initialize track
track = np.zeros(int(SAMPLE_RATE * DURATION))

# Bass line pattern (minimal, repeating every 2 bars)
# Using A minor scale
bass_notes = [110, 110, 165, 110, 146.83, 110, 165, 110]  # A, E, D, E pattern

# Pad chord progression (A minor - F major - G major - E minor)
pad_progressions = [
    [220, 264, 330],     # A minor (A, C, E)
    [174.61, 220, 261.63],  # F major (F, A, C)
    [196, 246.94, 293.66],  # G major (G, B, D)
    [164.81, 196, 246.94]   # E minor (E, G, B)
]

# Arpeggio pattern
arp_notes = [440, 550, 660, 550]  # A, C#, E, C# (higher octave)

print("Building drum pattern...")
# Add drums
current_time = 0
bar_count = 0
total_bars = int(DURATION / bar_duration)

for bar in range(total_bars):
    bar_count = bar

    # Kick on every beat (4/4)
    for beat in range(4):
        kick_time = bar * bar_duration + beat * beat_duration
        kick = generate_kick()
        add_to_track(track, kick, kick_time)

    # Hi-hats (closed on 8ths, open occasionally)
    for eighth in range(8):
        hihat_time = bar * bar_duration + eighth * (beat_duration / 2)

        # Open hi-hat on 4th and 8th eighth notes
        is_open = (eighth == 3 or eighth == 7) and bar % 4 == 3
        hihat = generate_hihat(closed=not is_open)
        add_to_track(track, hihat, hihat_time)

print("Adding bass line...")
# Add bass line (enters after 16 bars)
for bar in range(16, total_bars):
    for beat in range(4):
        bass_time = bar * bar_duration + beat * beat_duration
        note_idx = (beat + (bar % 2) * 4) % len(bass_notes)
        bass = generate_bass_note(bass_notes[note_idx], beat_duration * 0.9)
        add_to_track(track, bass, bass_time)

print("Adding atmospheric pads...")
# Add pads (enters after 32 bars, changes every 8 bars)
for bar in range(32, total_bars):
    if bar % 8 == 0:
        pad_idx = ((bar - 32) // 8) % len(pad_progressions)
        pad_time = bar * bar_duration
        pad = generate_pad(pad_progressions[pad_idx], bar_duration * 8)
        add_to_track(track, pad, pad_time)

print("Adding minimal arpeggios...")
# Add arpeggios (enters after 48 bars)
for bar in range(48, total_bars):
    if bar % 2 == 0:  # Every other bar
        for sixteenth in range(8):
            arp_time = bar * bar_duration + sixteenth * (beat_duration / 4)
            note_idx = sixteenth % len(arp_notes)
            arp = generate_arp_note(arp_notes[note_idx], beat_duration / 4 * 0.8)
            add_to_track(track, arp, arp_time)

print("Applying final processing...")
# Normalize
track = track / np.max(np.abs(track)) * 0.9

# Apply fade out in last 8 bars
fadeout_start = int((DURATION - bar_duration * 8) * SAMPLE_RATE)
fadeout_length = len(track) - fadeout_start
fade_curve = np.linspace(1, 0, fadeout_length)
track[fadeout_start:] *= fade_curve

# Apply fade in at start (first 2 bars)
fadein_length = int(bar_duration * 2 * SAMPLE_RATE)
fade_in_curve = np.linspace(0, 1, fadein_length)
track[:fadein_length] *= fade_in_curve

# Convert to 16-bit for WAV
track = (track * 32767).astype(np.int16)

# Save to file
output_file = "minimal_techno_track.wav"
sf.write(output_file, track, SAMPLE_RATE)

print(f"\n✓ Track generated successfully!")
print(f"✓ Saved to: {output_file}")
print(f"✓ Duration: {DURATION}s ({total_bars} bars)")
print(f"✓ Format: 16-bit WAV, {SAMPLE_RATE}Hz")
