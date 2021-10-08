import sys

def main(argv):
    fp = argv[0]
    if not fp.endswith('.txt'):
        print('File must be .txt!')
        return
    name = fp.split('/')[-1].split('.txt')[0]
    
    infile = open(fp, 'r')
    outfile = open(fp.split('.txt')[0] + '_c.txt', 'w')

    text = infile.read()
    outfile.write(text.replace('\n', ' '))
    
    infile.close()
    outfile.close()

if __name__ == '__main__':
    main(sys.argv[1:])
