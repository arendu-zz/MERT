__author__ = 'arenduchintala'


def get_upper_intersections(sort_seg):
    upper = []
    K = len(sort_seg)
    i = 0
    while i + 1 < K:
        points_to_lines = {}
        a = sort_seg[i]
        for j in xrange(i + 1, K):
            b = sort_seg[j]
            points_to_lines[intersect_point(a, b)] = j
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
    x = (a1[1] - a2[1]) / (a2[0] - a1[0])
    y = a1[0] * x + a1[1]
    return x, y, (a1[2], a2[2]) if a1[0] < a2[0]else (a2[2], a1[2]), a1[3]


if __name__ == '__main__':
    seg = [[-0.5, 2, '1 2 3 4', '1 3 2 1'], [-0.95, -1, 'e2', '1 3 2 1'], [0.2, 1, 'e3', '1 3 2 1'], [5, -40, 'e4', '1 3 2 1']]
    sorted_seg = sorted(seg)
    print get_upper_intersections(sorted_seg)
    print get_ranges(get_upper_intersections(sorted_seg))

