from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""

    return list(set(a.splitlines())&(set(b.splitlines())))


def sentences(a, b):
    """Return sentences in both a and b"""

    return list(set(sent_tokenize(a)).intersection(sent_tokenize(b)))


def substrings(a, b, n):
    # print([word[i:i+3] for i in range(0, len(word), 3)])
    """Return substrings of length n in both a and b"""
    sub = list(set([a[i:i + n] for i in range(len(a) - n + 1)]))
    l = []
    for w in sub:
        if w in b:
            l.append(w)
    return l
