# indent = tab
import sys
import json

def main(fn, offset=0):
	stm_path = ''
	words_path = ''

	stm_file = open(stm_path + fn + '.stm', 'r')
	stm_sents = stm_file.read().split('\n')[:-1]

	words_file = open(words_path + fn + '.json', 'r')
	words = json.load(words_file)

	trn_file = open(words_path + fn + '.txt', 'w')
    
	for sent in stm_sents:
		sent_words = []
		sent_start = float(sent.split()[3])
		sent_end = float(sent.split()[4])
		
		if len(words) == 0: break 
		while len(words) > 0 and words[0]['start']-float(offset) < sent_end + 1:
			word = words.pop(0)
			sent_words.append(word['word'])
		
		print('ref', ' '.join(sent.split()[5:]))
		print('hyp', ' '.join(sent_words))
		
		trn_file.write(' '.join(sent_words) + '\n')
		trn_file.flush()
	
	stm_file.close()
	words_file.close()
	trn_file.close()

if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2])
