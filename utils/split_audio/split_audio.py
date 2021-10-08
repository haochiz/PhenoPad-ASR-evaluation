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
	stm_path = ''
	audio_path = ''
	save_path = '' + fn + '/'
	
	# read stm file
	stm_file = open(stm_path + fn + '.stm', 'r')
	utt_list = stm_file.read().split('\n')[:-1]

	audio = audio_tools.load_wav(audio_path + fn + '.wav')

	for line in utt_list:
		utt = parse_utt_line(line)
		print(utt)
		
		if utt['end'] - utt['start'] <= 0.1:
			print('utt too short, continue')
			continue
		
		else:
			#normalize and save utt
			audio_seg = audio_tools.extract_normalize_seg(audio, utt['start'], utt['end'])
			name = '{}_{}_{}.wav'.format(fn, str(utt['start']), str(utt['end']))
			audio_tools.save_wav(save_path + name, audio_seg)

if __name__ == '__main__':
	main(sys.argv[1])
