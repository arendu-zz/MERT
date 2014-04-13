__author__ = 'arenduchintala'

import optparse
import sweep_line as sl
import bleu
import subprocess


def mid_point((x1, x2)):
    if x1 == float('-inf'):
        return x2 - 0.1
    if x2 == float('inf'):
        return x1 + 0.1
    return (x1 + x2) / 2.0


def sum_scores_per_range(rd, method):
    ranges_in_val = {}
    if method == 'bleu':
        for k, v in rd.items():
            stats = [0.0] * 10
            for hr_score, (hyp, ref) in v:
                stats = [stats[i] + hr_score[i] for i in xrange(10)]
            bs = bleu.bleu(stats)
            ranges_in_val[bs] = ranges_in_val.get(bs, [])
            ranges_in_val[bs].append(k)
    else:
        for k, v in rd.items():
            stats = 0.0
            for hr_score, (hyp, ref) in v:
                stats += hr_score
            ranges_in_val[stats] = ranges_in_val.get(stats, [])
            ranges_in_val[stats].append(k)
    return ranges_in_val


if __name__ == '__main__':
    optparser = optparse.OptionParser()
    optparser.add_option("-k", "--kbest-list", dest="input", default="data/train+dev.100best", help="100-best translation lists")
    optparser.add_option("-r", "--reference", dest="reference", default="data/train+dev.ref", help="Target language reference sentences")
    optparser.add_option("-l", "--lm", dest="lm", default=-1.0, type="float", help="Language model weight")
    optparser.add_option("-t", "--tm1", dest="tm1", default=-1.0, type="float", help="Translation model p(e|f) weight")
    optparser.add_option("-s", "--tm2", dest="tm2", default=-1.0, type="float", help="Lexical translation model p_lex(f|e) weight")
    optparser.add_option("-m", "--ef", dest="error_function", default="bleu", help="use bleu , editdistance or meteor")

    (opts, _) = optparser.parse_args()
    weights = {'p(e)': float(opts.lm), 'p(e|f)': float(opts.tm1), 'p_lex(f|e)': float(opts.tm2)}
    weights_cmd = {'p(e)': '-l', 'p(e|f)': '-t', 'p_lex(f|e)': '-s'}
    all_hyps = [pair.split(' ||| ') for pair in open(opts.input)]
    all_refs = [ref.strip() for ref in open(opts.reference)]
    num_sents = len(all_hyps) / 100
    ef = opts.error_function
    #permutations = it.permutations(weights.keys())
    print ''
    print '******************MERT Run Instance********************'
    print 'method:', opts.error_function
    print 'data train:', opts.input
    print 'data reference:', opts.reference
    print 'initial feature values:', weights
    for o in xrange(3):
        weights = {'p(e)': float(opts.lm), 'p(e|f)': float(opts.tm1), 'p_lex(f|e)': float(opts.tm2)}
        wts = list(weights.keys())
        for _ in xrange(o):
            wts.append(wts.pop(0))
        print ''
        print 'initial ordering:', wts
        for p in xrange(5):
            print ''
            print 'iteration', p
            for w in wts:
                inflexion_points = []
                for s in xrange(0, 400):
                    ref = all_refs[s]
                    hyps_for_one_sent = all_hyps[s * 100:s * 100 + 100]
                    hyp_lines = []
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
                                m = float(v)
                        hyp_lines.append((m, c, hyp, ref))

                    filtered_hyp_lines = sl.filter_highest_lines(hyp_lines)
                    sorted_hyp_lines = sorted(filtered_hyp_lines)
                    ip = sl.get_ranges(sl.get_upper_intersections(sorted_hyp_lines), method=ef)
                    inflexion_points += ip

                inflexion_points.sort()
                #pprint(inflexion_points)

                ranges = [(x1, x2) for x1, x2, hyp, ref in inflexion_points]
                range_markers_key = list(set(sl.chain(ranges)))
                range_markers_key.sort()
                #print '\nrange markers key\n', range_markers_key
                range_markers_dict = dict(
                    ((range_markers_key[i], range_markers_key[i + 1]), []) for i in xrange(len(range_markers_key) - 1))
                #print '\nrange markers_dict\n',
                #pprint(range_markers_dict)

                for (x1, x2, h, r) in inflexion_points:
                    for mx1, mx2 in sorted(range_markers_dict):
                        if x1 <= mx1 and mx2 <= x2:
                            range_markers_dict[mx1, mx2].append((h, r))

                #print 'line segments...'
                #pprint(range_markers_dict)
                score_ranges = sum_scores_per_range(range_markers_dict, method=ef)
                #print '\nrange markers bleu scores\n'
                #pprint(score_ranges)
                #for idx, k in enumerate(sorted(score_ranges, reverse=True)):
                #    print idx, 'max score', k, score_ranges[k]
                #    if idx == 5:
                #        break

                #print 'max score', max(score_ranges), 'max ranges', score_ranges[max(score_ranges)]
                print 'setting ', w, 'from', weights[w], 'to', mid_point(min(score_ranges[max(score_ranges)]))
                weights[w] = mid_point(min(score_ranges[max(score_ranges)]))

            info_str = 'info for trial:' + str(o) + '-' + str(p) + '\n' + 'weights:' + str(weights) + '\nmethod:' + ef
            cmd_opts = ' '.join([str(weights_cmd[i] + ' ' + str(weights[i])) for i in weights])
            #cmd = 'python rerank ' + cmd_opts + ' > outputs/' + str(o) + '-' + str(p) + '.out'
            #print cmd
            #subprocess.call(cmd)

            cmd2 = 'python rerank ' + cmd_opts + ' | python compute-bleu'
            print cmd2
            result = subprocess.check_output(cmd2, shell=True)
            print 'bleu on dev:', result
