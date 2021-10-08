# indent = tab
import sys
import numpy as np
from scipy.io.wavfile import write as wavwrite

from tools import audio_tools as audio_tools

def parse_utt_line(line):
	attributes = line.split()
	start = attributes[3]
	end = attributes[4]
	content = ' '.join(attributes[5:])
	return {'start': float(start), 'end': float(end), 'content': content}

def main(fn):
	end_pointer = 0.0

	stm_path = ''
	audio_path = ''
	save_path = ''
	# read stm file
	stm_file = open(stm_path + fn + '.stm', 'r')
	utt_list = stm_file.read().split('\n')[:-1]

	audio = audio_tools.load_wav(audio_path + fn + '.wav')

	for line in utt_list:
		utt = parse_utt_line(line)
		print(utt)
		
		if utt['end'] - utt['start'] <= 0.3:
			print('utt too short, continue')
			continue
		if utt['end'] <= end_pointer:
			print('overlap, continue')
			continue
		
		if utt['start'] >= end_pointer:
			audio = audio_tools.normalize_seg(audio, utt['start'], utt['end'])
		else:
			utt['start'] = end_pointer
			if utt['end'] - utt['start'] < 0.5: 
                        	print('utt too short, continue')
                        	continue

			audio = audio_tools.normalize_seg(audio, utt['start'], utt['end'])
		
		# update end_pointer
		end_pointer = utt['end']		
	
	# save normalized audio file
	wavwrite(save_path + fn + '.wav', 16000, audio.astype(np.int16))


if __name__ == '__main__':
	main(sys.argv[1])
