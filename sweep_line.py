__author__ = 'arenduchintala'
from pprint import pprint


def chain(points):
    for p in points:
        yield p[0]
        yield p[1]


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


def get_ranges(upper):
    upper_range = []
    for idx, (x, y, (h1, h2), href) in enumerate(upper):
        if idx == 0:
            upper_range.append((float('-inf'), x, h1, href))
        else:
            upper_range.append((xp, x, h1, href))
        xp = x
    #the last segment goes all the way to +infinity
    upper_range.append((x, float('inf'), h2, href))
    return upper_range


def intersect_point(a1, a2):
    #m = 0
    #c = 1
    #hyp = 2
    #ref = 3
    try:
        x = (a1[1] - a2[1]) / (a2[0] - a1[0])
    except:
        print 'returning none...', a1, a2
        return None, None, (None, None), None
    y = a1[0] * x + a1[1]
    #return None, None, (None, None), None
    return x, y, (a1[2], a2[2]) if a1[0] < a2[0]else (a2[2], a1[2]), a1[3]


if __name__ == '__main__':
    seg = [[-0.5, 2, 'A1', 'ref'], [-0.95, -1, 'B1', 'ref'], [0.2, 1, 'C1', 'ref'], [5, -40, 'D1', 'ref']]
    seg2 = [[-0.15, 2, 'A2', 'ref2'], [-1.95, -1, 'B2', 'ref2'], [1.2, 1, 'C2', 'ref2'], [0.5, -40, 'D2', 'ref2']]
    segs = [seg, seg2]

    inflexion_points = []
    for s in segs:
        sorted_seg = sorted(s)
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

    print '\nrange markers filled\n',
    pprint(range_markers_dict)