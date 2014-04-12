__author__ = 'arenduchintala'

import optparse
from pprint import pprint
import sweep_line as sl
import bleu


def compute_bleu_ranges(range_marker):
    bleu_range_markers = {}
    print 'computing bleu ranges...'
    for k, v in range_marker.items():
        stats = [0 for i in xrange(10)]
        for (h, r) in v:
            stats = [sum(scores) for scores in zip(stats, bleu.bleu_stats(h, r))]
        bs = bleu.bleu(stats)
        bleu_range_markers[bs] = k
    return bleu_range_markers


if __name__ == '__main__':
    optparser = optparse.OptionParser()
    optparser.add_option("-k", "--kbest-list", dest="input", default="data/train.100best", help="100-best translation lists")
    optparser.add_option("-r", "--reference", dest="reference", default="data/train.ref", help="Target language reference sentences")
    optparser.add_option("-l", "--lm", dest="lm", default=-1.0, type="float", help="Language model weight")
    optparser.add_option("-t", "--tm1", dest="tm1", default=-0.5, type="float", help="Translation model p(e|f) weight")
    optparser.add_option("-s", "--tm2", dest="tm2", default=-0.5, type="float", help="Lexical translation model p_lex(f|e) weight")
    (opts, _) = optparser.parse_args()
    weights = {'p(e)': float(opts.lm), 'p(e|f)': float(opts.tm1), 'p_lex(f|e)': float(opts.tm2)}
    all_hyps = [pair.split(' ||| ') for pair in open(opts.input)]
    all_refs = [ref.strip() for ref in open(opts.reference)]
    num_sents = len(all_hyps) / 100

    for w in weights:
        print 'current weights', weights
        inflexion_points = []
        for s in xrange(0, 100):
            ref = all_refs[s]
            hyps_for_one_sent = all_hyps[s * 100:s * 100 + 100]
            lines = []
            for (num, hyp, feats) in hyps_for_one_sent:
                #compute c and m
                c = 0.0
                m = 0.0
                for feat in feats.split(' '):
                    (k, v) = feat.split('=')
                    if k != w:
                        c += weights[k] * float(v)
                    else:
                        #compute m
                        m += weights[k] * float(v)
                lines.append((m, c, hyp, ref))
            sorted_lines = sorted(lines)
            ip = sl.get_ranges(sl.get_upper_intersections(sorted_lines))
            inflexion_points += ip

        inflexion_points.sort()
        pprint(inflexion_points)
        print '\n'
        ranges = [(x1, x2) for x1, x2, hyp, ref in inflexion_points]
        range_markers_key = list(set(sl.chain(ranges)))
        range_markers_key.sort()
        print '\nrange markers key\n', range_markers_key
        range_markers_dict = dict(((range_markers_key[i], range_markers_key[i + 1]), []) for i in xrange(len(range_markers_key) - 1))
        #range_markers_dict[(inflexion_points[-1][0], inflexion_points[-1][1])] = []
        print '\nrange markers_dict\n',
        pprint(range_markers_dict)

        for (x1, x2, h, r) in inflexion_points:
            for mx1, mx2 in sorted(range_markers_dict):
                if x1 <= mx1 and mx2 <= x2:
                    range_markers_dict[mx1, mx2].append((h, r))

        print 'line segments...'
        #pprint(range_markers_dict)
        print 'bleu score for ranges...'
        bleu_ranges = compute_bleu_ranges(range_markers_dict)
        print max(bleu_ranges), bleu_ranges[max(bleu_ranges)]
        weights[w] = (bleu_ranges[max(bleu_ranges)][0] + bleu_ranges[max(bleu_ranges)][1]) / 2
        print 'setting ', w, 'to', weights[w]
    print 'final weights', weights