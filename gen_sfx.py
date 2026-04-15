import wave
import struct
import math
import os

def generate_beep(filename, duration_ms=50, freq=600, sample_rate=44100, volume=0.3):
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    # Open the wave file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            # short envelope for clickiness
            envelope = 1.0 - (i / num_samples) 
            # Square wave like retro beep
            t = float(i) / sample_rate
            value = math.sin(2 * math.pi * freq * t)
            # make it square by thresholding, or keep sine
            value = 1.0 if value > 0 else -1.0
            
            # apply volume and envelope
            value = value * volume * envelope * 32767
            
            # Pack as 16-bit signed integer
            wav_file.writeframesraw(struct.pack('<h', int(value)))

generate_beep('nav.wav')
print("Generated nav.wav")

def generate_select(filename, duration_ms=150, freq=800, sample_rate=44100, volume=0.3):
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) # Mono
        wav_file.setsampwidth(2) # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Pitch slide up
            current_freq = freq + (i / num_samples) * 400
            value = math.sin(2 * math.pi * current_freq * t)
            value = 1.0 if value > 0 else -1.0
            envelope = 1.0 - (i / num_samples)**2
            value = value * volume * envelope * 32767
            wav_file.writeframesraw(struct.pack('<h', int(value)))

generate_select('select.wav')
print("Generated select.wav")
