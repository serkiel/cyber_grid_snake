import wave
import struct
import math
import random

def generate_crash(filename, duration_ms=250, sample_rate=44100, volume=0.4):
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            # Noise burst
            value = random.uniform(-1.0, 1.0)
            
            # Envelope (decay quickly)
            envelope = math.exp(-6.0 * (i / num_samples))
            
            value = value * volume * envelope * 32767
            wav_file.writeframesraw(struct.pack('<h', int(value)))

generate_crash('crash.wav')
print("Generated crash.wav")
