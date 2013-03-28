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
    for num, doc in enumerate(parser.find_all('doc')):
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
        target_line = text[line]
        current_offset = offset[line]
        target_segment = target_line[start + current_offset:end + current_offset]
        if line == end_line and re.match('[\.!\?]', target_segment) is None:
            correction = re.sub(r"(.+)([\.!\?])(.+)", lambda m: "%s <|punct=%s|> %s" % (m.group(1), m.group(2), m.group(3)), correction)
            new_offset = len(correction) - (end - start)
            print "%s --> %s, delta = %d" % (target_segment, correction, new_offset)
            text[line] = target_line[:start + current_offset] + correction + target_line[end + current_offset:]
            offset[line] += new_offset
            return text, offset
        else:
            return text, offset

    def split_by_sentences(text):
        """
        assumes that the first index is the title, next lines are paragraphs
        """
        by_sentence = []
        for paragraph in text:
            split = re.split('([\\.!\\?])\\s+([A-Z])', paragraph)
            if len(split) > 1:
                sentences = [split[0] + split[1] + "\n"]
                for x in split[2:]:
                    if re.match('^[\.!\?]$', x):
                        sentences.append("%s%s\n" % (cur_sentence.lstrip(), x))
                    elif re.match('^[A-Z]$', x):
                        cur_sentence = x
                    else:
                        cur_sentence = cur_sentence + x
                sentences.append('%s\n' % cur_sentence.lstrip())
            else:
                # this is a title without punctuation
                sentences = [split[0]]
            by_sentence += sentences + ['\n']

        return by_sentence

    nonempty = lambda x: re.match('^\s+$', x) is None and x != ''
    parser = BeautifulSoup(open(filename))
    try:
        text = parser.find('text').get_text().split('\n')
    except:
        return

    text = filter(nonempty, text)
    original = [s.lstrip() for s in text]
    # deep copy
    corrected = [a for a in original]
    offset = {x:0 for x in xrange(len(corrected))}
    for mistake in parser.find_all('mistake'):
        print offset
        c = mistake.findChild('correction')
        if c:
            c = c.get_text().strip()
            corrected, offset = corrected_text(offset = offset, text = corrected, correction = c, **mistake.attrs)

    f1 = codecs.open('%s-original' % filename, 'w', 'UTF-8')
    f2 = codecs.open('%s-corrected' % filename, 'w', 'UTF-8')
    original = split_by_sentences(original)
    corrected = split_by_sentences(corrected)
    try:
        f1.writelines(original)
        f2.writelines(corrected)
    except:
        import ipdb
        ipdb.set_trace()
    f1.close()
    f2.close()