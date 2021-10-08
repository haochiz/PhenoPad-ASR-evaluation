# indent = tab
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize

def manual_lemmatize(sent):
	sent = sent.replace('\'re', ' are')
	sent = sent.replace('\'ve', ' have')
	sent = sent.replace('\'ll', ' will')
	sent = sent.replace('yep', 'yes').replace('yup', 'yes').replace('yeah', 'yes')

	return sent

def lemmatize_word(word, lemmatizer):
	#print(pos_tag(word_tokenize(word))[0][1])
	if pos_tag(word_tokenize(word))[0][1][0] == 'V':
		#output = lemmatizer.lemmatize(word, pos=str.lower(pos_tag(word_tokenize(word))[0][1][0]))
		output = lemmatizer.lemmatize(word, pos ='v')
	elif pos_tag(word_tokenize(word))[0][1][0] == 'N':
		output = lemmatizer.lemmatize(word, pos ='n')
	else:
		output = lemmatizer.lemmatize(word)
	return output

def lemmatize_sentence(sent, lemmatizer):
	outputs = []
	sent = manual_lemmatize(sent.lower())
	for word in sent.split():
		outputs.append(lemmatize_word(word, lemmatizer))
	return ' '.join(outputs)

def lemmatize_sentence_with_filter(sent, lemmatizer):
	outputs = []
	sent = manual_lemmatize(sent.lower())
	for word in sent.split():
		if word in ['um', 'er', 'uh', 'mhm', 'oh', 'ah', 'mm']: continue
		outputs.append(lemmatize_word(word, lemmatizer))
	return ' '.join(outputs)

if __name__ == '__main__':
	sent = str.lower('')
	lemmatizer = WordNetLemmatizer()
	print(sent)
	print(lemmatize_sentence(sent, lemmatizer))
