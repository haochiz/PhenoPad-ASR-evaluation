#! /usr/bin/env python3
import unicodedata

class Utterance(object):
    def __init__(self, start=None, end=None, speaker=None, content=None):
        self.start = start
        self.end = end
        self.speaker = speaker
        self.content = content
        
        self.span = None
    
    def timestamps2sec(self):
        # check if the timestamps are valid
        if not is_timestamp(self.start) or not is_timestamp(self.end):
            raise ValueError('Timestamp(s) Invalid!')
        # convert timestamps
        start_min, start_sec = int(self.start.split(':')[0]), int(self.start.split(':')[1])
        end_min, end_sec = int(self.end.split(':')[0]), int(self.end.split(':')[1])
        return (start_min*60 + start_sec, end_min*60 + end_sec)

def read_txt(fn, in_path):
    with open(in_path + fn + '.txt', 'r') as f:
        raw_trn_txt = f.read()
    return raw_trn_txt

def split_utt(text):
    return text.split('\n\n')

def is_timestamp(string):
    digitlist = [c for c in string if c.isdigit()]
    return True if ( float(len(digitlist)) / float(len(string)) ) >= 0.75 else False

def main(fn, in_path, out_path):
    trn_file = open(out_path + fn + '.trn', 'w')
    # read raw trn text
    raw_trn_txt = read_txt(fn, in_path)
    # split into utterances
    utt_list = split_utt(raw_trn_txt)

    #print(utt_list)
    utt_objs = []
    # parse utts
    for utt_i, utt in enumerate(utt_list):
        utt = utt.split('\xc2\xa0')
        print(utt)
        utt_obj = Utterance()
        # find time span and speaker
        utt_obj.start = utt[0].replace('\n', '')
        utt_obj.speaker = [ c for c in utt[1].split(':')[0] if c.isdigit() ][0]
        utt_obj.content = utt[1].split(':')[1][1:]
        utt_obj.end = utt[2].replace('\n', '')

        print(utt_obj.__dict__)
        print('\n')
        
        # format utterance to trn
        speaker_id = fn + '-' + utt_obj.speaker
        utt_id = speaker_id + '-' + str(utt_i)
        trn_utt = '{} ({})\n'.format(utt_obj.content, utt_id)
        print(trn_utt)
        trn_file.write(trn_utt)
        trn_file.flush()
        
        utt_objs.append(utt_obj)
    
    trn_file.close()    
    print(len(utt_objs))    

if __name__ == '__main__':
    in_path = ''
    out_path = ''
    fn = ''
    main(fn, in_path, out_path)


