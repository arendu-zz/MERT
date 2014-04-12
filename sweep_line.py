__author__ = 'arenduchintala'
from pprint import pprint
import bleu
import metrics


def chain(points):
    for p in points:
        yield p[0]
        yield p[1]


def sum_bleu_scores_per_range(range_marker_dict):
    range_bleu_scores = {}
    for k, v in range_markers_dict.items():
        sum_bs = 0.0
        for h, r in v:
            b_stats = bleu.bleu_stats(h, r)
            bs = bleu.bleu(b_stats)
            sum_bs += bs
        range_bleu_scores[k] = sum_bs
    return range_bleu_scores


def get_upper_intersections(sort_seg):
    upper = []
    K = len(sort_seg)
    i = 0
    while i + 1 < K:
        points_to_lines = {}
        a = sort_seg[i]
        for j in xrange(i + 1, K):
            b = sort_seg[j]
            intersect = intersect_point(a, b)
            if intersect[0] is not None and intersect[1] is not None:
                points_to_lines[intersect] = j
            else:
                print 'skipping intersection...', a, b, intersect
                pass
        (mx, my, mhyp_pair, ref) = min(points_to_lines)
        upper.append((mx, my, mhyp_pair, ref))
        i = points_to_lines[(mx, my, mhyp_pair, ref)]
    return upper


def get_score(h, r):
    #return metrics.get_ed_score(h, r)
    return metrics.get_bleu_score(h, r)
    #return metrics.get_meteor_score(h, r)


def get_ranges(upper):
    upper_range = []
    for idx, (x, y, (h1, h2), href) in enumerate(upper):
        if idx == 0:
            upper_range.append((float('-inf'), x, get_score(h1, href), (h1, href)))
        else:
            upper_range.append((xp, x, get_score(h1, href), (h1, href)))
        xp = x
    #the last segment goes all the way to +infinity
    upper_range.append((x, float('inf'), get_score(h2, href), (h2, href)))
    return upper_range


def intersect_point(a1, a2):
    #m = 0
    #c = 1
    #hyp = 2
    #ref = 3
    x = (a1[1] - a2[1]) / (a2[0] - a1[0])
    y = a1[0] * x + a1[1]
    return x, y, (a1[2], a2[2]) if a1[0] < a2[0]else (a2[2], a1[2]), a1[3]


def filter_highest_lines(segs):
    slopes_to_max_intercept = {}
    for m, c, h, r in segs:
        if m in slopes_to_max_intercept:
            if c > slopes_to_max_intercept[m][1]:
                slopes_to_max_intercept[m] = [m, c, h, r]
        else:
            slopes_to_max_intercept[m] = [m, c, h, r]
    return slopes_to_max_intercept.values()


if __name__ == '__main__':
    seg = [[-0.5, 2, 'A1', 'R1'], [-0.5, -1, 'B1', 'R1'], [0.2, 1, 'C1', 'R1'], [5, -40, 'D1', 'R1']]
    #seg2 = [[-0.15, 2, 'A2', 'R2'], [-1.95, -1, 'B2', 'R2'], [1.2, 1, 'C2', 'R2'], [0.5, -40, 'D2', 'R2']]
    segs = [seg]

    inflexion_points = []
    for s in segs:
        print s
        filter_seg = filter_highest_lines(s)
        print filter_seg
        sorted_seg = sorted(filter_seg)
        print sorted_seg
        inflexion_points += get_ranges(get_upper_intersections(sorted_seg))

    inflexion_points.sort()
    pprint(inflexion_points)
    print '\n'
    ranges = [(x1, x2) for x1, x2, hyp, ref in inflexion_points]
    range_markers_key = list(set(chain(ranges)))
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

    print '\nrange markers filled\n'
    pprint(range_markers_dict)

    #print '\nrange markers bleu scores\n'
    #pprint(sum_bleu_scores_per_range(range_markers_dict))