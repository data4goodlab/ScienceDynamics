import turicreate.aggregate as agg
import itertools
from collections import Counter
import pycld2 as cld2


def get_column_count_sframe(sf, col_name, sort_by_count=True):
    g = sf.groupby(col_name, {'Count': agg.COUNT()})
    if sort_by_count:
        g = g.sort("Count")
    return g


def filter_sframe_by_func(sf, filter_func):
    """
    Filter Sframe using a filter function
    :param sf: SFrame object
    :param filter_func: a function that return 1 for the lines we want to keep and 0 for the lines we want to filter out
    :return: filtered SFrame
    :rtype: gl.SFrame
    """
    if filter_func is None:
        return sf

    return sf[sf.apply(lambda r: filter_func(r))]


def join_all_lists(list_of_lists):
    return list(itertools.chain.from_iterable(list_of_lists))


def count_value_in_dict_values_lists(d, value):
    """
    Given dict with list as values the function count how many times a value appear in these value lists
    :param d: dict with lists as value
    :param value: value to count
    :return: the number of times a value appears in the dict values
    :rtype: int
    """
    l = join_all_lists(d.values())
    c = Counter(l)
    if value in c:
        return c[value]
    return 0


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)


def detect_lang(t):
    """
    Detect the input text language using cld2 package.
    :param t: input text
    :return: return string with the name of the detected language or None if no language was detected
    :rtype: str
    """
    try:
        return cld2.detect(t, bestEffort=True)[2][0][0].lower()
    except:
        return None
