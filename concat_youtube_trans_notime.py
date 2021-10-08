import sys

ref_dir = ''

def main(name):
	print('processing ' + name)
	in_file = open(ref_dir + name + '.txt', 'r')
	out_file = open(ref_dir + 'concat/' + name  + '.txt', 'w')
	in_text = in_file.read()
	#in_text = in_text.replace('\xc2\xa0', ' ')
	
	out_text = in_text.replace('\n', ' ')
	print(out_text)
	out_file.write(out_text)
	out_file.flush()

	in_file.close()
	out_file.close()


if __name__ == '__main__':
	name = sys.argv[1]
	main(name)
