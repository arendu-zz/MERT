__author__ = 'arenduchintala'


def sweep_line(sort_seg):
    upper = []
    K = len(sort_seg)
    i = 0
    while i + 1 < K:
        points_to_lines = {}
        a = sort_seg[i]
        for j in xrange(i + 1, K):
            b = sort_seg[j]
            points_to_lines[intersect_point(a, b)] = j
        (mx, my) = min(points_to_lines)
        upper.append((mx, my))
        i = points_to_lines[mx, my]
    return upper


def intersect_point(a1, a2):
    #m = 0
    #c = 1
    #x = 2
    #t = 3
    x = (a1[1] - a2[1]) / (a2[0] - a1[0])
    y = a1[0] * x + a1[1]
    return x, y


if __name__ == '__main__':
    seg = [[-0.5, 2, float('-inf')], [-0.95, -1, float('-inf')], [0.2, 1, float('-inf')], [5, -40, float('-inf')]]
    sorted_seg = sorted(seg)
    print sweep_line(sorted_seg)