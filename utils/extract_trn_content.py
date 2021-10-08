#! /usr/bin/env python3
# indent = space

import unicodedata
import sys

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
        start_min, start_sec = int(self.start.split(':')[0]), float(self.start.split(':')[1])
        end_min, end_sec = int(self.end.split(':')[0]), float(self.end.split(':')[1])
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
    content_file = open(out_path + fn + '.txt', 'w')
    # read raw trn text
    raw_trn_txt = read_txt(fn, in_path)
    # split into utterances
    utt_list = split_utt(raw_trn_txt)

    #print(utt_list)
    utt_objs = []
    # parse utts
    for utt in utt_list:
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
        
        # format utterance to stm
        channel = 'A' # assume only 1 channel for now
        speaker_id = fn + '-' + utt_obj.speaker
        stm_utt = '{} {} {} {} {} {}\n'.format(fn, channel, speaker_id, utt_obj.timestamps2sec()[0], utt_obj.timestamps2sec()[1], utt_obj.content)
        print(stm_utt)
        content_file.write(utt_obj.content + '\n')
        content_file.flush()
        
        utt_objs.append(utt_obj)
    
    content_file.close()    
    print(len(utt_objs))    

if __name__ == '__main__':
    in_path = ''
    out_path = ''
    fn = sys.argv[1]
    main(fn, in_path, out_path)


