__author__ = 'arenduchintala'
import editdistance as ed
import bleu


def R(h, ref):
    hnr = len(h.intersection(ref))
    r = len(ref)
    return float(hnr) / r


def P(h, ref):
    hnr = len(h.intersection(ref))
    h = len(h)
    return float(hnr) / h


def get_meteor_score(h, ref, alpha=0.5):
    h = set(h.split())
    ref = set(ref.split())
    prec = P(h, ref)
    recall = R(h, ref)
    if recall == 0 and prec == 0:
        return 0.0
    return prec * recall / (((1 - alpha) * recall) + (alpha * prec))


def get_ed_score(h, r):
    h = h.split()
    r = r.split()
    return ed.edratio(h, r)


def get_bleu_stats(h, r):
    h = h.split()
    r = r.split()
    stats = [0 for i in xrange(10)]
    stats = [sum(scores) for scores in zip(stats, bleu.bleu_stats(h, r))]
    return stats



