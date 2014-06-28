import itertools
from itertools import starmap
from cytoolz.utils import raises
from functools import partial
from cytoolz.itertoolz import (remove, groupby, merge_sorted,
                             concat, concatv, interleave, unique,
                             isiterable,
                             mapcat, isdistinct, first, second,
                             nth, take, drop, interpose, get,
                             rest, last, cons, frequencies,
                             reduceby, iterate, accumulate,
                             sliding_window, count, partition,
                             partition_all, take_nth, pluck, join)
from cytoolz.compatibility import range, filter
from operator import add, mul


def identity(x):
    return x


def iseven(x):
    return x % 2 == 0


def isodd(x):
    return x % 2 == 1


def inc(x):
    return x + 1


def double(x):
    return 2 * x


def test_remove():
    r = remove(iseven, range(5))
    assert type(r) is not list
    assert list(r) == list(filter(isodd, range(5)))


def test_groupby():
    assert groupby(iseven, [1, 2, 3, 4]) == {True: [2, 4], False: [1, 3]}


def test_merge_sorted():
    assert list(merge_sorted([1, 2, 3], [1, 2, 3])) == [1, 1, 2, 2, 3, 3]
    assert list(merge_sorted([1, 3, 5], [2, 4, 6])) == [1, 2, 3, 4, 5, 6]
    assert list(merge_sorted([1], [2, 4], [3], [])) == [1, 2, 3, 4]
    assert list(merge_sorted([5, 3, 1], [6, 4, 3], [],
                             key=lambda x: -x)) == [6, 5, 4, 3, 3, 1]
    assert list(merge_sorted([2, 1, 3], [1, 2, 3],
                             key=lambda x: x // 3)) == [2, 1, 1, 2, 3, 3]
    assert list(merge_sorted([2, 3], [1, 3],
                             key=lambda x: x // 3)) == [2, 1, 3, 3]
    assert ''.join(merge_sorted('abc', 'abc', 'abc')) == 'aaabbbccc'
    assert ''.join(merge_sorted('abc', 'abc', 'abc', key=ord)) == 'aaabbbccc'
    assert ''.join(merge_sorted('cba', 'cba', 'cba',
                                key=lambda x: -ord(x))) == 'cccbbbaaa'
    assert list(merge_sorted([1], [2, 3, 4], key=identity)) == [1, 2, 3, 4]


def test_interleave():
    assert ''.join(interleave(('ABC', '123'))) == 'A1B2C3'
    assert ''.join(interleave(('ABC', '1'))) == 'A1BC'


def test_unique():
    assert tuple(unique((1, 2, 3))) == (1, 2, 3)
    assert tuple(unique((1, 2, 1, 3))) == (1, 2, 3)
    assert tuple(unique((1, 2, 3), key=iseven)) == (1, 2)


def test_isiterable():
    assert isiterable([1, 2, 3]) is True
    assert isiterable('abc') is True
    assert isiterable(5) is False


def test_isdistinct():
    assert isdistinct([1, 2, 3]) is True
    assert isdistinct([1, 2, 1]) is False

    assert isdistinct("Hello") is False
    assert isdistinct("World") is True

    assert isdistinct(iter([1, 2, 3])) is True
    assert isdistinct(iter([1, 2, 1])) is False


def test_nth():
    assert nth(2, 'ABCDE') == 'C'
    assert nth(2, iter('ABCDE')) == 'C'
    assert nth(1, (3, 2, 1)) == 2
    assert nth(0, {'foo': 'bar'}) == 'foo'
    assert raises(StopIteration, lambda: nth(10, {10: 'foo'}))


def test_first():
    assert first('ABCDE') == 'A'
    assert first((3, 2, 1)) == 3
    assert isinstance(first({0: 'zero', 1: 'one'}), int)


def test_second():
    assert second('ABCDE') == 'B'
    assert second((3, 2, 1)) == 2
    assert isinstance(second({0: 'zero', 1: 'one'}), int)


def test_last():
    assert last('ABCDE') == 'E'
    assert last((3, 2, 1)) == 1
    assert isinstance(last({0: 'zero', 1: 'one'}), int)


def test_rest():
    assert list(rest('ABCDE')) == list('BCDE')
    assert list(rest((3, 2, 1))) == list((2, 1))


def test_take():
    assert list(take(3, 'ABCDE')) == list('ABC')
    assert list(take(2, (3, 2, 1))) == list((3, 2))


def test_drop():
    assert list(drop(3, 'ABCDE')) == list('DE')
    assert list(drop(1, (3, 2, 1))) == list((2, 1))


def test_take_nth():
    assert list(take_nth(2, 'ABCDE')) == list('ACE')


def test_get():
    assert get(1, 'ABCDE') == 'B'
    assert list(get([1, 3], 'ABCDE')) == list('BD')
    assert get('a', {'a': 1, 'b': 2, 'c': 3}) == 1
    assert get(['a', 'b'], {'a': 1, 'b': 2, 'c': 3}) == (1, 2)

    assert get('foo', {}, default='bar') == 'bar'
    assert get({}, [1, 2, 3], default='bar') == 'bar'
    assert get([0, 2], 'AB', 'C') == ('A', 'C')

    assert get([0], 'AB') == ('A',)

    assert raises(IndexError, lambda: get(10, 'ABC'))
    assert raises(KeyError, lambda: get(10, {'a': 1}))
    assert raises(TypeError, lambda: get({}, [1, 2, 3]))
    assert raises(TypeError, lambda: get([1, 2, 3], 1, None))


def test_mapcat():
    assert (list(mapcat(identity, [[1, 2, 3], [4, 5, 6]])) ==
            [1, 2, 3, 4, 5, 6])

    assert (list(mapcat(reversed, [[3, 2, 1, 0], [6, 5, 4], [9, 8, 7]])) ==
            list(range(10)))

    inc = lambda i: i + 1
    assert ([4, 5, 6, 7, 8, 9] ==
            list(mapcat(partial(map, inc), [[3, 4, 5], [6, 7, 8]])))


def test_cons():
    assert list(cons(1, [2, 3])) == [1, 2, 3]


def test_concat():
    assert list(concat([[], [], []])) == []
    assert (list(take(5, concat([['a', 'b'], range(1000000000)]))) ==
            ['a', 'b', 0, 1, 2])


def test_concatv():
    assert list(concatv([], [], [])) == []
    assert (list(take(5, concatv(['a', 'b'], range(1000000000)))) ==
            ['a', 'b', 0, 1, 2])


def test_interpose():
    assert "a" == first(rest(interpose("a", range(1000000000))))
    assert "tXaXrXzXaXn" == "".join(interpose("X", "tarzan"))
    assert list(interpose(0, itertools.repeat(1, 4))) == [1, 0, 1, 0, 1, 0, 1]
    assert list(interpose('.', ['a', 'b', 'c'])) == ['a', '.', 'b', '.', 'c']


def test_frequencies():
    assert (frequencies(["cat", "pig", "cat", "eel",
                        "pig", "dog", "dog", "dog"]) ==
            {"cat": 2, "eel": 1, "pig": 2, "dog": 3})
    assert frequencies([]) == {}
    assert frequencies("onomatopoeia") == {"a": 2, "e": 1, "i": 1, "m": 1,
                                           "o": 4, "n": 1, "p": 1, "t": 1}


def test_reduceby():
    data = [1, 2, 3, 4, 5]
    iseven = lambda x: x % 2 == 0
    assert reduceby(iseven, add, data, 0) == {False: 9, True: 6}
    assert reduceby(iseven, mul, data, 1) == {False: 15, True: 8}

    projects = [{'name': 'build roads', 'state': 'CA', 'cost': 1000000},
                {'name': 'fight crime', 'state': 'IL', 'cost': 100000},
                {'name': 'help farmers', 'state': 'IL', 'cost': 2000000},
                {'name': 'help farmers', 'state': 'CA', 'cost': 200000}]
    assert reduceby(lambda x: x['state'],
                    lambda acc, x: acc + x['cost'],
                    projects, 0) == {'CA': 1200000, 'IL': 2100000}


def test_reduce_by_init():
    assert reduceby(iseven, add, [1, 2, 3, 4]) == {True: 2 + 4, False: 1 + 3}


def test_iterate():
    assert list(itertools.islice(iterate(inc, 0), 0, 5)) == [0, 1, 2, 3, 4]
    assert list(take(4, iterate(double, 1))) == [1, 2, 4, 8]


def test_accumulate():
    assert list(accumulate(add, [1, 2, 3, 4, 5])) == [1, 3, 6, 10, 15]
    assert list(accumulate(mul, [1, 2, 3, 4, 5])) == [1, 2, 6, 24, 120]


def test_accumulate_works_on_consumable_iterables():
    assert list(accumulate(add, iter((1, 2, 3)))) == [1, 3, 6]


def test_sliding_window():
    assert list(sliding_window(2, [1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]
    assert list(sliding_window(3, [1, 2, 3, 4])) == [(1, 2, 3), (2, 3, 4)]


def test_sliding_window_of_short_iterator():
    assert list(sliding_window(3, [1, 2])) == []


def test_partition():
    assert list(partition(2, [1, 2, 3, 4])) == [(1, 2), (3, 4)]
    assert list(partition(3, range(7))) == [(0, 1, 2), (3, 4, 5)]
    assert list(partition(3, range(4), pad=-1)) == [(0, 1, 2),
                                                    (3, -1, -1)]
    assert list(partition(2, [])) == []


def test_partition_all():
    assert list(partition_all(2, [1, 2, 3, 4])) == [(1, 2), (3, 4)]
    assert list(partition_all(3, range(5))) == [(0, 1, 2), (3, 4)]
    assert list(partition_all(2, [])) == []


def test_count():
    assert count((1, 2, 3)) == 3
    assert count([]) == 0
    assert count(iter((1, 2, 3, 4))) == 4

    assert count('hello') == 5
    assert count(iter('hello')) == 5


def test_pluck():
    assert list(pluck(0, [[0, 1], [2, 3], [4, 5]])) == [0, 2, 4]
    assert list(pluck([0, 1], [[0, 1, 2], [3, 4, 5]])) == [(0, 1), (3, 4)]
    assert list(pluck(1, [[0], [0, 1]], None)) == [None, 1]

    data = [{'id': 1, 'name': 'cheese'}, {'id': 2, 'name': 'pies', 'price': 1}]
    assert list(pluck('id', data)) == [1, 2]
    assert list(pluck('price', data, None)) == [None, 1]
    assert list(pluck(['id', 'name'], data)) == [(1, 'cheese'), (2, 'pies')]
    assert list(pluck(['name'], data)) == [('cheese',), ('pies',)]
    assert list(pluck(['price', 'other'], data, None)) == [(None, None),
                                                           (1, None)]

    assert raises(IndexError, lambda: list(pluck(1, [[0]])))
    assert raises(KeyError, lambda: list(pluck('name', [{'id': 1}])))


def test_join():
    names = [(1, 'one'), (2, 'two'), (3, 'three')]
    fruit = [('apple', 1), ('orange', 1), ('banana', 2), ('coconut', 2)]

    def addpair(pair):
        return pair[0] + pair[1]

    result = set(starmap(add, join(first, names, second, fruit)))

    expected = set([((1, 'one', 'apple', 1)),
                    ((1, 'one', 'orange', 1)),
                    ((2, 'two', 'banana', 2)),
                    ((2, 'two', 'coconut', 2))])

    print(result)
    print(expected)
    assert result == expected


def test_key_as_getter():
    squares = [(i, i**2) for i in range(5)]
    pows = [(i, i**2, i**3) for i in range(5)]

    assert set(join(0, squares, 0, pows)) == set(join(lambda x: x[0], squares,
                                                      lambda x: x[0], pows))

    get = lambda x: (x[0], x[1])
    assert set(join([0, 1], squares, [0, 1], pows)) == set(join(get, squares,
                                                                get, pows))

    get = lambda x: (x[0],)
    assert set(join([0], squares, [0], pows)) == set(join(get, squares,
                                                          get, pows))


def test_join_double_repeats():
    names = [(1, 'one'), (2, 'two'), (3, 'three'), (1, 'uno'), (2, 'dos')]
    fruit = [('apple', 1), ('orange', 1), ('banana', 2), ('coconut', 2)]

    result = set(starmap(add, join(first, names, second, fruit)))

    expected = set([((1, 'one', 'apple', 1)),
                    ((1, 'one', 'orange', 1)),
                    ((2, 'two', 'banana', 2)),
                    ((2, 'two', 'coconut', 2)),
                    ((1, 'uno', 'apple', 1)),
                    ((1, 'uno', 'orange', 1)),
                    ((2, 'dos', 'banana', 2)),
                    ((2, 'dos', 'coconut', 2))])

    print(result)
    print(expected)
    assert result == expected


def test_join_missing_element():
    names = [(1, 'one'), (2, 'two'), (3, 'three')]
    fruit = [('apple', 5), ('orange', 1)]

    result = list(join(first, names, second, fruit))
    print(result)
    result = set(starmap(add, result))

    expected = set([((1, 'one', 'orange', 1))])

    assert result == expected


def test_left_outer_join():
    result = set(join(identity, [1, 2], identity, [2, 3], left_default=None))
    expected = set([(2, 2), (None, 3)])

    print(result)
    print(expected)
    assert result == expected


def test_right_outer_join():
    result = set(join(identity, [1, 2], identity, [2, 3], right_default=None))
    expected = set([(2, 2), (1, None)])

    assert result == expected


def test_outer_join():
    result = set(join(identity, [1, 2], identity, [2, 3],
                      left_default=None, right_default=None))
    expected = set([(2, 2), (1, None), (None, 3)])

    assert result == expected
