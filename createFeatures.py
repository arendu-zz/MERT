__author__ = 'arenduchintala'

import optparse
import unicodedata


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    optparser = optparse.OptionParser()
    optparser.add_option("-k", "--kbest-list", dest="kbest", default="data/train+dev.100best", help="100-best translation lists")
    optparser.add_option("-s", "--source", dest="source", default="data/train+dev.src", help="Target language reference sentences")
    (opts, _) = optparser.parse_args()
    all_source = [src.split('|||')[1].strip() for src in open(opts.source)]
    all_hyps = [pair.split(' ||| ') for pair in open(opts.kbest)]

    writer = open(str(opts.kbest) + '.new.feats', 'w')
    for s in xrange(0, len(all_source)):
        src = all_source[s]
        src_tokens = src.split()
        src_type = set(src_tokens)
        src_len = len(src_tokens)
        hyps_for_one_sent = all_hyps[s * 100:s * 100 + 100]
        for (num, hyp, feats) in hyps_for_one_sent:
            hyp_tokens = hyp.split()
            hyp_types = set(hyp_tokens)
            hyp_len = len(hyp_tokens)
            len_ratio = float(hyp_len) / float(src_len)
            untranslated_tokens = src_type.intersection(hyp_types)
            #print untranslated_tokens
            untranslated_tokens = [token for token in untranslated_tokens if (len(token) > 1 and not is_number(token))]
            ut_length = len(untranslated_tokens)
            #if len(untranslated_tokens) > 1:
            #    print 'filter', untranslated_tokens
            #    print src
            #    print hyp
            #    print feats
            lrf = ' ' + 'lr=' + str(len_ratio)
            utf = ' ' + 'ut=' + str(len(untranslated_tokens))
            new_feats = feats.strip() + lrf + utf
            new_line = num + ' ||| ' + hyp.strip() + ' ||| ' + new_feats.strip() + '\n'
            writer.write(new_line)
    writer.flush()
    writer.close()
    print

