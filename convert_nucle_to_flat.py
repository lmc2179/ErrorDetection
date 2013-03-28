import codecs
from bs4 import BeautifulSoup
import re

__all__ = ['split_by_doc', 'flatten_doc']

def split_by_doc(filename):
    """
    saves memory by processing each doc one by one, the full thing takes 600mb of memory while in the parser, so is 
    super slow. This will also help split into a dev + train set. Returns number of docs.
    """
    parser = BeautifulSoup(open(filename))
    for num, doc in enumerate(a.find_all('doc')):
        with codecs.open('doc_%d' % num, 'w', 'UTF-8') as f:
            f.write(unicode(doc.prettify()))
    return num

def flatten_doc(filename):
    """
    convert a single entry, denoted by a <doc></doc> into two outfiles, the original and the corrected, as files w/
    one line per sentence and no extraneous tags
    """
    def corrected_text(offset, text, end_off, end_par, start_off, start_par, correction):
        line = int(start_par)
        end_line = int(end_par)
        start = int(start_off)
        end = int(end_off)
        if line == end_line:
            target_line = text[line]
            current_offset = offset[line]
            new_offset = len(correction) - (end - start)
            print "%s --> %s, delta = %d" % (target_line[start + current_offset:end + current_offset], correction, new_offset)
            text[line] = target_line[:start + current_offset] + correction + target_line[end + current_offset:]
            offset[line] += new_offset
            return text, offset
        else:
            return text, offset

    def split_by_sentences(text):
        """
        assumes that the first index is the title, next lines are paragraphs
        """
        by_sentence = [text[0]]
        for paragraph in text[0:]:
            sentences = ["%s.\n" % x.lstrip() for x in paragraph.split('.') if x != '']
            by_sentence += sentences + ['\n']

        return by_sentence

    nonempty = lambda x: re.match('^\s+$', x) is None and x != ''
    parser = BeautifulSoup(open(filename))
    text = filter(nonempty, parser.find('text').get_text().split('\n'))
    original = [s.lstrip() for s in text]
    # deep copy
    corrected = [a for a in original]
    offset = {x:0 for x in xrange(1,len(corrected))}
    for mistake in parser.find_all('mistake'):
        print offset
        c = mistake.findChild('correction').get_text().strip()
        corrected, offset = corrected_text(offset = offset, text = corrected, correction = c, **mistake.attrs)

    f1 = open('%s-original' % filename, 'w')
    f2 = open('%s-corrected' % filename, 'w')
    f1.writelines(split_by_sentences(original))
    f2.writelines(split_by_sentences(corrected))
    f1.close()
    f2.close()