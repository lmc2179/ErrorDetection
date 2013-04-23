import codecs
from sh import mkdir,ls
from copy import deepcopy
from nltk.tokenize import wordpunct_tokenize
from bs4 import BeautifulSoup

def split_ann(ann_file):
    if 'tmp' not in ls():
        mkdir('tmp')
    parser = BeautifulSoup(open(ann_file))
    for mistake in parser.find_all('mistake'):
        with open('tmp/%s' % mistake.attrs['nid'], 'a') as f:
            f.write(mistake.__str__())


def multi_write(conll_file, flat, corr,ann_dir = 'tmp'):
    with open(conll_file) as conll, codecs.open(flat, 'w', 'utf-8') as f1, codecs.open(corr,'w', 'utf-8') as out:
        cur_doc = []
        cur_par = []
        cur_sentence = []
        prev_doc = 829
        prev_par = 0
        end = False
        conll_it = conll.__iter__()
        for line in conll_it:
            s = line.strip().split()
            if s == []:
                try: 
                    n = conll_it.next().strip().split()
                except StopIteration:
                    end = True
                if int(n[0]) != prev_doc or end:
                    # new document, analyze previous document and write to files
                    cur_par.append(cur_sentence)
                    cur_doc.append(cur_par)
                    try:
                        mistake_file = open("%s/%d" % (ann_dir, prev_doc))
                    except:
                        mistake_file = ""
                    b = BeautifulSoup(mistake_file)
                    corrected = deepcopy(cur_doc)
                    for mistake in b.find_all('mistake'):
                        pid, sid, s, e = int(mistake.attrs['pid']), int(mistake.attrs['sid']), int(mistake.attrs['start_token']), int(mistake.attrs['end_token'])
                        try:
                            corrected[pid][sid][s:e] = wordpunct_tokenize(mistake.find('correction').text.decode('utf-8'))
                        except:
                            import ipdb; ipdb.set_trace()
                    if [len(p) for p in cur_doc] != [len(p) for p in corrected]:
                        import ipdb
                        ipdb.set_trace()
                    to_st = lambda m: u"\n\n".join([u"\n".join(s) for s in [[u" ".join(s) for s in p] for p in m]])
                    f1.write(u"%s\n" % to_st(cur_doc))
                    out.write(u"%s\n" % to_st(corrected))
                    prev_doc = int(n[0])
                    cur_sentence = [n[4].decode('utf-8')]
                    cur_par = []
                    cur_doc = []
                    prev_par = 0
                    continue
                elif int(n[1]) != prev_par:
                    # new paragraph, same document
                    for i in xrange(int(n[1]) - prev_par - 1):
                        cur_doc.append([])
                    cur_par.append(cur_sentence)
                    cur_doc.append(cur_par)
                    cur_par = []
                    cur_sentence = [n[4].decode('utf-8')]
                    prev_par = int(n[1])
                    continue
                else:
                    # new sentence
                    cur_par.append(cur_sentence)
                    cur_sentence = [n[4].decode('utf-8')]
                    continue

            else:
                cur_sentence.append(s[4].decode('utf-8'))
