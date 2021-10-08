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
        if len(self.start.split(':')[1]) < 3 and len(self.end.split(':')[1]) < 3 : return 'No Timestamp'
        elif len(self.start.split(':')[1]) != len(self.end.split(':')[1]): raise Exception('Timestamp incomplete!')
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

def merge_untimestamped_utterances(utt1, utt2):
    ''' add utt2's content to target utterance utt1
    ''' 
    utt1.content = utt1.content + ' ' + utt2.content
    return utt1

def main(fn, in_path, out_path):
    stm_file = open(out_path + fn + '.stm', 'w')
    # read raw trn text
    raw_trn_txt = read_txt(fn, in_path)
    # split into utterances
    utt_list = split_utt(raw_trn_txt)

    last_end = 0 # the end of the last timestamped utt
    pending_utt = None

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
        
        if type(utt_obj.timestamps2sec()) is str:
            # if no pending utt (last utt was timestamped)
            if not pending_utt:
                pending_utt = utt_obj
            else:
                # merge utts
                pending_utt = merge_untimestamped_utterances(pending_utt, utt_obj)
                
        else:
            # if no pending utt (last utt was timestamped)
            if not pending_utt:
                # format utterance to stm
                channel = 'A' # assume only 1 channel for now
                speaker_id = fn + '-' + utt_obj.speaker
                stm_utt = '{} {} {} {} {} {}\n'.format(fn, channel, speaker_id, utt_obj.timestamps2sec()[0], utt_obj.timestamps2sec()[1], utt_obj.content)
                print(stm_utt)
                stm_file.write(stm_utt)
                stm_file.flush()
        
                utt_objs.append(utt_obj)
                # update last ending timestamp
                last_end = utt_obj.timestamps2sec()[1]
            else:
                # save pending utt
                channel = 'A' # assume only 1 channel for now
                speaker_id = fn + '-' + pending_utt.speaker
                stm_utt = '{} {} {} {} {} {}\n'.format(fn, channel, speaker_id, last_end, utt_obj.timestamps2sec()[0], pending_utt.content) # start and the end of the last timestamped                                                                                                                                            # utt; end at the beginning of the next utt
                print(stm_utt)
                stm_file.write(stm_utt)
                stm_file.flush()
                
                utt_objs.append(utt_obj)
                # update last ending timestamp and clear pending_utt
                last_end = utt_obj.timestamps2sec()[1]
                pending_utt = None
                # format utterance to stm
                channel = 'A' # assume only 1 channel for now
                speaker_id = fn + '-' + utt_obj.speaker
                stm_utt = '{} {} {} {} {} {}\n'.format(fn, channel, speaker_id, utt_obj.timestamps2sec()[0], utt_obj.timestamps2sec()[1], utt_obj.content)
                print(stm_utt)
                stm_file.write(stm_utt)
                stm_file.flush()
        
                utt_objs.append(utt_obj)
                # update last ending timestamp
                last_end = utt_obj.timestamps2sec()[1]
                

    stm_file.close()    
    print(len(utt_objs))    

if __name__ == '__main__':
    in_path = ''
    out_path = ''
    fn = sys.argv[1]
    main(fn, in_path, out_path)


