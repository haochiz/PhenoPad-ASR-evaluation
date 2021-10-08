import sys

result_dir = '/home/jixuan/kaldi_models/evaluation_audio_files/youtube_audio/kaldi/'

def get_sentence(line):
	print(line)
	return line.split('::')[1]

def main(name):
	print('processing ' + name)
	in_file = open(result_dir + name + '.txt', 'r')
	out_file = open(result_dir + 'concat/' + name  + '.txt', 'w')
	in_text = in_file.read()
	#in_text = in_text.replace('\xc2\xa0', ' ')
	
	lines = in_text.split('\n')[:-1]
	out_lines = []
	
	for line in lines:
		sent = get_sentence(line)
		out_lines.append(sent)

	out_text = ' '.join(out_lines)
	print(out_text)
	out_file.write(out_text)
	out_file.flush()

	in_file.close()
	out_file.close()


if __name__ == '__main__':
	name = sys.argv[1]
	main(name)
