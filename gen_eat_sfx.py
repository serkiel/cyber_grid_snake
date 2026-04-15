import wave
import struct
import math
import os

def generate_eat(filename, duration_ms=100, freq=1200, sample_rate=44100, volume=0.3):
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Pitch modulation for an Arcade 'gulp' or 'coin'
            # Frequency swoops quickly from high to higher
            current_freq = freq + (i / num_samples) * 800
            value = math.sin(2 * math.pi * current_freq * t)
            # Make it square
            value = 1.0 if value > 0 else -1.0
            # Envelope, fast decay
            envelope = math.exp(-6.0 * (i / num_samples))
            value = value * volume * envelope * 32767
            wav_file.writeframesraw(struct.pack('<h', int(value)))

generate_eat('eat.wav')
print("Generated eat.wav")
