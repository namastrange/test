#!/usr/bin/env python3
"""
Pure Percussion Techno Track Generator
5-6 minute percussion-only track with swing and organic instruments
Inspired by Bliss Inc, Adam Pits
"""

import numpy as np
import soundfile as sf
from scipy import signal

# Audio parameters
SAMPLE_RATE = 44100
BPM = 128
DURATION = 330  # 5.5 minutes
SWING_AMOUNT = 0.15  # 15% swing

# Calculate timing
beat_duration = 60.0 / BPM
bar_duration = beat_duration * 4
sixteenth_duration = beat_duration / 4

def apply_swing(position, swing=SWING_AMOUNT):
    """Apply swing to timing positions (0-based 16th note position)"""
    if position % 2 == 1:  # Delay odd 16th notes
        return swing * sixteenth_duration
    return 0

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
    """Generate a techno kick drum with optional pitch variance"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Pitch envelope
    base_pitch = 45 + pitch_variance
    pitch_env = base_pitch + 95 * np.exp(-t * 18)
    phase = np.cumsum(2 * np.pi * pitch_env / SAMPLE_RATE)
    kick = np.sin(phase)

    # Amplitude envelope
    amp_env = np.exp(-t * 10)
    kick = kick * amp_env

    # Add punch
    click = np.exp(-t * 120) * 0.35
    kick = kick + click

    return kick * 0.75

def generate_snare(duration=0.15):
    """Generate techno snare"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Tone component
    tone_freq = 180 + 200 * np.exp(-t * 30)
    phase = np.cumsum(2 * np.pi * tone_freq / SAMPLE_RATE)
    tone = np.sin(phase) * 0.4

    # Noise component
    noise = np.random.randn(len(t))
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

    noise = np.random.randn(len(t))

    # High-pass filter
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

def generate_clap(duration=0.1):
    """Generate hand clap"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Multiple bursts for clap texture
    noise = np.random.randn(len(t))

    # Filter for body
    sos = signal.butter(2, [500, 4000], 'bp', fs=SAMPLE_RATE, output='sos')
    clap = signal.sosfilt(sos, noise)

    # Multi-burst envelope
    env = np.exp(-t * 30)
    burst1 = env
    burst2 = np.roll(env, int(0.01 * SAMPLE_RATE)) * 0.7
    burst3 = np.roll(env, int(0.02 * SAMPLE_RATE)) * 0.5

    clap = clap * (burst1 + burst2 + burst3) / 2.2

    return clap * 0.25

def generate_cowbell(pitch=800, duration=0.2):
    """Generate cowbell"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Metallic tone with inharmonic partials
    tone = np.sin(2 * np.pi * pitch * t)
    tone += 0.5 * np.sin(2 * np.pi * pitch * 2.3 * t)
    tone += 0.3 * np.sin(2 * np.pi * pitch * 3.7 * t)

    # Band-pass for metallic character
    sos = signal.butter(2, [600, 3000], 'bp', fs=SAMPLE_RATE, output='sos')
    cowbell = signal.sosfilt(sos, tone)

    # Sharp envelope
    env = np.exp(-t * 20)
    cowbell = cowbell * env

    return cowbell * 0.15

def add_to_track(track, audio, start_time):
    """Add audio to track at specified time"""
    start_sample = int(start_time * SAMPLE_RATE)
    end_sample = start_sample + len(audio)

    if end_sample > len(track):
        audio = audio[:len(track) - start_sample]
        end_sample = len(track)

    if start_sample < len(track):
        track[start_sample:end_sample] += audio

print("Generating pure percussion techno track...")
print(f"BPM: {BPM}, Swing: {SWING_AMOUNT*100}%, Duration: {DURATION}s ({DURATION/60:.1f} minutes)")

# Initialize track
track = np.zeros(int(SAMPLE_RATE * DURATION))
total_bars = int(DURATION / bar_duration)

print("Building layered percussion arrangement...")

# Section markers
intro_end = 16
build1_end = 32
drop1_end = 64
breakdown_end = 96
build2_end = 112
drop2_end = 144
outro_start = 144

for bar in range(total_bars):
    bar_start = bar * bar_duration

    # 4/4 KICK - solid four on the floor
    if bar >= 0:
        for beat in [0, 4, 8, 12]:  # Quarter notes (16th note positions)
            kick_time = bar_start + beat * sixteenth_duration
            variance = np.random.uniform(-1, 1) if bar >= build1_end else 0
            kick = generate_kick(pitch_variance=variance)
            add_to_track(track, kick, kick_time)

    # SNARE - on 2 and 4
    if bar >= 8:
        for beat in [4, 12]:  # Beats 2 and 4
            snare_time = bar_start + beat * sixteenth_duration + apply_swing(beat)
            snare = generate_snare()
            add_to_track(track, snare, snare_time)

    # Additional snare fills during builds
    if build1_end <= bar < drop1_end and bar % 8 >= 6:
        for beat in [7, 10, 14]:
            snare_time = bar_start + beat * sixteenth_duration + apply_swing(beat)
            snare = generate_snare()
            add_to_track(track, snare * 0.7, snare_time)

    # HI-HATS - 16th notes with swing
    if bar >= 4:
        for pos in range(16):
            # Skip some during breakdown for dynamics
            if breakdown_end <= bar < build2_end and pos % 4 == 2:
                continue

            hihat_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
            is_closed = pos % 4 != 2  # Open on off-beats
            is_accent = pos % 4 == 0
            hihat = generate_hihat(closed=is_closed, accent=is_accent)
            add_to_track(track, hihat, hihat_time)

    # TABLA GE (bass tabla)
    if bar >= 12:
        if bar % 2 == 0:
            tabla_pattern = [2, 10]
        else:
            tabla_pattern = [1, 6, 13]

        for pos in tabla_pattern:
            tabla_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
            pitch = 200 + np.random.uniform(-10, 10)
            tabla = generate_tabla_ge(pitch=pitch)
            add_to_track(track, tabla, tabla_time)

    # TABLA NA (treble tabla) - active during drops
    if (drop1_end <= bar < breakdown_end) or (drop2_end <= bar):
        if bar % 2 == 1:
            for pos in [3, 7, 11, 15]:
                tabla_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
                tabla = generate_tabla_na()
                add_to_track(track, tabla, tabla_time)

    # RIM SHOTS - accents and fills
    if bar >= 20:
        if bar % 8 == 7:  # Fill at end of 8-bar phrases
            for pos in [8, 10, 12, 14]:
                rim_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
                rim = generate_rim()
                add_to_track(track, rim, rim_time)
        elif bar % 4 == 2:  # Occasional accents
            for pos in [6, 14]:
                rim_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
                rim = generate_rim()
                add_to_track(track, rim, rim_time)

    # SHAKERS - texture throughout
    if bar >= 24:
        for pos in range(1, 16, 2):  # Odd 16ths
            if np.random.random() > 0.25:  # 75% probability
                shaker_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
                shaker = generate_shaker()
                add_to_track(track, shaker, shaker_time)

    # CLAPS - during drops and builds
    if (build1_end <= bar < drop1_end) or (build2_end <= bar < drop2_end):
        for beat in [4, 12]:  # On snare beats
            clap_time = bar_start + beat * sixteenth_duration + apply_swing(beat)
            clap = generate_clap()
            add_to_track(track, clap, clap_time)

    # COWBELL - occasional flavor during second half
    if bar >= drop1_end and bar % 16 == 0:
        cowbell_pattern = [0, 3, 6, 9]
        for pos in cowbell_pattern:
            cowbell_time = bar_start + pos * sixteenth_duration + apply_swing(pos)
            cowbell = generate_cowbell()
            add_to_track(track, cowbell, cowbell_time)

    # BREAKDOWN section - reduce to just kick and occasional percussion
    if breakdown_end <= bar < build2_end:
        # Kick continues, other elements are already reduced above
        pass

print("Applying final processing...")
# Normalize
track = track / np.max(np.abs(track)) * 0.90

# Fade in (first 4 bars)
fadein_length = int(bar_duration * 4 * SAMPLE_RATE)
fade_in_curve = np.linspace(0, 1, fadein_length)
track[:fadein_length] *= fade_in_curve

# Fade out (last 8 bars)
fadeout_start = int((DURATION - bar_duration * 8) * SAMPLE_RATE)
fadeout_length = len(track) - fadeout_start
fade_curve = np.linspace(1, 0, fadeout_length)
track[fadeout_start:] *= fade_curve

# Convert to 16-bit
track = (track * 32767).astype(np.int16)

# Save
output_file = "minimal_techno_track.wav"
sf.write(output_file, track, SAMPLE_RATE)

print(f"\n✓ Track generated successfully!")
print(f"✓ Saved to: {output_file}")
print(f"✓ Style: Pure percussion techno with swing")
print(f"✓ Duration: {DURATION}s ({DURATION/60:.1f} minutes, {total_bars} bars)")
print(f"✓ Time signature: 4/4")
print(f"✓ Percussion: Kick, snare, hi-hats, tablas, rims, shakers, claps, cowbell")
print(f"✓ Format: 16-bit WAV, {SAMPLE_RATE}Hz")
