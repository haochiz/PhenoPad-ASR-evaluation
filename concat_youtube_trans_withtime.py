import sys

ref_dir = '/home/jixuan/kaldi_models/evaluation_audio_files/youtube_audio/ref/'

def is_sentence(line):
	if line[0].isdigit() and line[-1].isdigit():
		return False
	else:
		return True
		

def main(name):
	print('processing ' + name)
	in_file = open(ref_dir + name + '.txt', 'r')
	out_file = open(ref_dir + 'concat/' + name  + '.txt', 'w')
	in_text = in_file.read()
	in_text = in_text.replace('\xc2\xa0', ' ')
	
	lines = in_text.split('\n\n')
	out_lines = []
	
	for line in lines:
		if is_sentence(line):
			out_lines.append(line)

	out_text = ' '.join(out_lines)
	print(out_text)
	out_file.write(out_text)
	out_file.flush()

	in_file.close()
	out_file.close()


if __name__ == '__main__':
	name = sys.argv[1]
	main(name)
