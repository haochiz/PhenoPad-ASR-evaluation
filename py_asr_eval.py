# indent = tab
# requires python 3.5+
import subprocess
import re
import sys

import nltk
from nltk.stem import WordNetLemmatizer

ref_dir = ''
hyp_dir = ''
result_dir = ''

lemmatizer = WordNetLemmatizer()

def dedigit(sent):
	digidict = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five',\
		    '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '0': 'zero', '10': 'ten', '30': 'thirty', '50': 'fifty'}
	for k in digidict:
		sent = sent.replace(k, digidict[k])
	return sent

def standardize(sent):
	word_map = {'\'ll': ' will', '\'re': ' are',\
		    'alright': 'all right', 'gonna': 'going to', 'mum': 'mom', 'okay': 'ok',\
		    'yeah': 'yes'}
	for k in word_map:
		sent = sent.replace(k, word_map[k])
	return sent

def lemmatize_sentence(sent):
	word_list = nltk.word_tokenize(sent)
	word_list = [lemmatizer.lemmatize(w, 'v') for w in word_list]
	word_list = [lemmatizer.lemmatize(w, 'n') for w in word_list]
	lemmatized_output = ' '.join(word_list)
	return lemmatized_output

def normalize_sentence(sent):
	# remove '.' '_' '-' etc.
	sent = sent.lower()
	norm_sent = sent.replace('.', '').replace('_', '').replace('-', ' ').replace('???', '')
	# remove tokens for kaldi
	norm_sent = norm_sent.replace('<unk>', '').replace('[noise]', '').replace('[laughter]', '') 
	# remove 'uh' 'um' 'oh' 
	norm_sent = norm_sent.replace('uh', '').replace('um', '').replace('oh', '')
	# replace alternative form with standard form (e.g. alright vs. all right, gonna vs going to, etc.)
	norm_sent = standardize(norm_sent)
	# convert digit
	norm_sent = dedigit(norm_sent)
	# lemmatize
	norm_sent = lemmatize_sentence(norm_sent)

	return norm_sent

def main(fn):
	ref = open(ref_dir + fn + '.txt', 'r')
	hyp = open(hyp_dir + fn +'.txt', 'r')

	ref_sents = ref.read().split('\n')
	hyp_sents = hyp.read().split('\n')

	print(len(ref_sents), len(hyp_sents))
	print(ref.name, hyp.name)
	
	ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')	
	
	session_dict = {}
	sents_list = []
	for i in range(min(len(ref_sents), len(hyp_sents))):
		sent_dict = {}
		# write sent to temp file
		with open('ref_temp.txt', 'w') as rt:
			rt.write(normalize_sentence(ref_sents[i]))
		with open('hyp_temp.txt', 'w') as ht: 
			ht.write(normalize_sentence(hyp_sents[i]))
		
		# eval sent
		sent_result = subprocess.run('wer -i -a -c ref_temp.txt hyp_temp.txt'.split(), stdout=subprocess.PIPE)

		# format result
		result_stdout = sent_result.stdout.decode('utf-8')
		if 'SENTENCE 1' in result_stdout:
			sent_dict['instances'] = ansi_escape.sub('', result_stdout.split('SENTENCE 1\n')[0])
			result_lines = result_stdout.split('SENTENCE 1\n')[1].split('\n')
			# summary
			sent_dict['correct_words'] = int(result_lines[0].split('(')[0].split('%')[1])
			sent_dict['error_words'] = int(result_lines[1].split('(')[0].split('%')[1])
			sent_dict['total_words'] = sent_dict['correct_words'] + sent_dict['error_words']
			# err types
			modes = {'insert': [], 'delete': [], 'sub': [], 'None':[]}
			mode = 'None'
			for l in result_lines:
				if 'INSERTIONS' in l: 
					mode = 'insert'
					continue
				elif 'DELETIONS' in l:
					mode = 'delete'
					continue
				elif 'SUBSTITUTIONS' in l:
					mode = 'sub'
					continue
				elif 'Sentence count' in l:
					break
				modes[mode].append(l)
			
			sent_dict['insertions'] = '\n'.join(modes['insert'])
			sent_dict['deletions'] = '\n'.join(modes['delete'])
			sent_dict['substitutions'] = '\n'.join(modes['sub'])
			
			sent_dict['insertions_count'], sent_dict['deletions_count'], sent_dict['substitutions_count'] = 0, 0, 0
			for il in modes['insert']:
				sent_dict['insertions_count'] += int(il.split()[1])
			for dl in modes['delete']:
				sent_dict['deletions_count'] += int(dl.split()[1]) 	
			for sl in modes['sub']:
				sent_dict['substitutions_count'] += int(sl.split('-> ')[1].split()[1])
				
			sents_list.append(sent_dict)
	
	# summarize results
	session_dict['words_count'], session_dict['err_count'] = 0, 0
	session_dict['inserts_count'], session_dict['deletes_count'], session_dict['subs_count'] = 0, 0, 0
	for d in sents_list:
		session_dict['words_count'] += d['total_words']
		session_dict['err_count'] += d['error_words']
		session_dict['inserts_count'] += d['insertions_count']
		session_dict['deletes_count'] += d['deletions_count']
		session_dict['subs_count'] += d['substitutions_count']
	
	with open(result_dir + fn + '.txt', 'w') as of:
		of.write('Total: {}, Err: {}, WER: {:.1f}%, Ins: {}, Del: {}, Sub: {}\n\n'.format(session_dict['words_count'], session_dict['err_count'], session_dict['err_count']/session_dict['words_count']*100, session_dict['inserts_count'], session_dict['deletes_count'], session_dict['subs_count']))
		for si, sent in enumerate(sents_list):
			of.write('Sentence {}:\n'.format(si+1))
			of.write('Total: {}, Err: {}, WER: {:.1f}%, Ins: {}, Del: {}, Sub: {}\n'.format(sent['total_words'], sent['error_words'], sent['error_words']/sent['total_words']*100, sent['insertions_count'], sent['deletions_count'], sent['substitutions_count']))
			of.write(sent['instances'])
			of.write('INS:\n' + sent['insertions'] + '\n')
			of.write('DEL:\n' + sent['deletions'] + '\n')
			of.write('SUB:\n' + sent['substitutions'] + '\n\n')

if __name__ == '__main__':
	fn = sys.argv[1]
	main(fn)

