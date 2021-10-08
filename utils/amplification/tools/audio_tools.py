# indent = tab
import numpy as np
from scipy.io.wavfile import read as wavread

import wave

def load_wav(fn):
	audio = wavread(fn)
	return np.array(audio[1],dtype=float)

def extract_seg(audio, start, end, rate=16000):
	start_frame, end_frame = int(start*rate), int(end*rate)
	return audio[start_frame:end_frame]

def normalize(audio, rms_target=2000):
	'''
	Normalize audio signal to a specified rms level
	Args:
        - audio: audio np array
        - rms_level(int): rms level in dB
	'''
	# linear rms level and scaling factor
	rms = np.sqrt(np.mean(audio**2))
	print(rms)
	if rms >= rms_target: return audio
	
	# normalize
	peak = max( abs(max(audio)), abs(min(audio)) ) # find the peaked value of 
	a = min(rms_target/rms, 32767.0/peak)
	y = (audio * a)

	print(a)
	print(np.sqrt(np.mean(y**2)))
	return y 

def normalize_seg(audio, start, end, rate=16000):
	start_frame, end_frame = int(start*rate), int(end*rate)
	seg = audio[start_frame:end_frame]
	seg_ = normalize(seg)
	audio[start_frame:end_frame] = seg_
	return audio

if __name__ == '__main__':
	# test
	a = wavread('path/to/dir/' + '.wav')
	print(np.array(a[1],dtype=float))
	print(np.array(a[1],dtype=float).shape)
	
	b = wave.open('path/to/dir/' + '.wav')
	samples = b.getnframes()
	audio = b.readframes(samples)
	audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
	audio_as_np_float32 = audio_as_np_int16.astype(np.float32)
	print(audio_as_np_float32.shape)
