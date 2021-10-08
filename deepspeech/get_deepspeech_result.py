# requires python3.6+
# indent = space

import subprocess
import json
import re

#NOTE edit here
MODEL_PATH = './'
MODEL_NAME = 'deepspeech-0.7.4-models.pbmm'
SCORER_PATH = './'
SCORER_NAME = 'deepspeech-0.7.4-models.scorer'

AUDIO_PATH = ''
TRN_STM_PATH = '' # stm transcripts dir
TRN_SENT_PATH = '' # reference dir
RESULT_PATH = './deepspeech_results/' 

EVAL_RESULT_PATH = './eval_results/'

def get_words(fn):
    words = subprocess.run(('deepspeech --model {} --scorer {} --audio {} --json'.format(MODEL_PATH+MODEL_NAME, SCORER_PATH+SCORER_NAME, AUDIO_PATH+fn+'.wav')).split(), stdout=subprocess.PIPE)
    words = json.loads(words.stdout.decode('utf-8'))
    return words

def words_to_sents(fn, words, offset=0):
    stm_file = open(TRN_STM_PATH + fn + '.stm', 'r')
    stm_sents = stm_file.read().split('\n')[:-1]
    
    words = words['transcripts'][0]['words']
    
    result_file = open(RESULT_PATH + fn + '.txt', 'w')
    
    for sent in stm_sents:
        sent_words = []
        sent_start = float(sent.split()[3])
        sent_end = float(sent.split()[4])
        #print('sentence span: {}-{}'.format(sent_start, sent_end))

        if len(words) == 0: break
	#NOTE testing
        print('words[0]', words[0])
        while len(words) > 0 and words[0]['start_time']-float(offset) < sent_end + 1:
            word = words.pop(0)
            sent_words.append(word['word'])

        print('ref', ' '.join(sent.split()[5:]))
        print('hyp', ' '.join(sent_words))

        result_file.write(' '.join(sent_words) + '\n')
        result_file.flush()

    stm_file.close()
    result_file.close()

def evaluate(fn):
	ref = open(TRN_SENT_PATH + fn + '.txt', 'r')
	hyp = open(RESULT_PATH + fn +'.txt', 'r')

	ref_sents = ref.read().split('\n')
	#hyp_sents = hyp.read().split('\n')
	hyp_sents = hyp.read().replace('\n\n', '\n').split('\n')	

	print(len(ref_sents), len(hyp_sents))
	print(ref.name, hyp.name)
	
	ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')	
	
	session_dict = {}
	sents_list = []
	for i in range(min(len(ref_sents), len(hyp_sents))):
		sent_dict = {}
		# write sent to temp file
		with open('ref_temp.txt', 'w') as rt:
			rt.write(ref_sents[i])
		with open('hyp_temp.txt', 'w') as ht: 
			ht.write(hyp_sents[i])
		
		# eval sent
		sent_result = subprocess.run('wer -i -a -c ref_temp.txt hyp_temp.txt'.split(), stdout=subprocess.PIPE)
		#print(sent_result.stdout.decode('utf-8'))

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
	
	with open(EVAL_RESULT_PATH + fn + '.txt', 'w') as of:
		of.write('Total: {}, Err: {}, WER: {:.1f}%, Ins: {}, Del: {}, Sub: {}\n\n'.format(session_dict['words_count'], session_dict['err_count'], session_dict['err_count']/session_dict['words_count']*100, session_dict['inserts_count'], session_dict['deletes_count'], session_dict['subs_count']))
		for si, sent in enumerate(sents_list):
			of.write('Sentence {}:\n'.format(si+1))
			of.write('Total: {}, Err: {}, WER: {:.1f}%, Ins: {}, Del: {}, Sub: {}\n'.format(sent['total_words'], sent['error_words'], sent['error_words']/sent['total_words']*100, sent['insertions_count'], sent['deletions_count'], sent['substitutions_count']))
			of.write(sent['instances'])
			of.write('INS:\n' + sent['insertions'] + '\n')
			of.write('DEL:\n' + sent['deletions'] + '\n')
			of.write('SUB:\n' + sent['substitutions'] + '\n\n') 

if __name__ == '__main__':
    #audio_files = {'2019_01_30_0': 0, '2019_03_20_1': 0, '2019_04_10_0': 0, '2019_04_25_0': 10, '2019_11_28_0': -1, '2019_12_05_0': 0, '2019_12_05_1': 0,\
    #               '2020_03_04_0': 3, '2020_03_04_1': 0, '2020_03_04_2': 0, '2020_03_04_3': 0, '2020_03_04_4': 0, '2020_03_04_5': 0, '2020_03_04_6': 0,\
    #               '2020_03_04_7': 8, '2020_03_04_8': 134, '2020_03_06_0': 0, '2020_03_06_1': 0, '2020_03_06_2': 0, '2020_03_06_3': 0, '2020_03_06_4': 0,\
    #               '2020_03_06_5': 0, '2020_03_06_6': 0, '2020_03_06_7': 0, '2020_03_06_8': 0}
    for fn in audio_files:
        words = get_words(fn)
        words_to_sents(fn, words, offset=audio_files[fn]) 
        evaluate(fn)

