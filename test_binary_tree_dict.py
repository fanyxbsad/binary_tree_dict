"""Unit and property-based tests for immutable binary tree dictionary."""

import itertools
import unittest

from hypothesis import given
from hypothesis import strategies as st

from binary_tree_dict import (
    BinaryTreeDict,
    concat,
    cons,
    empty,
    filter_lst,
    find,
    from_list,
    iterator,
    length,
    map_lst,
    member,
    reduce_lst,
    remove,
    reverse,
    to_list,
)


class TestBinaryTreeDict(unittest.TestCase):
    """Tests for BinaryTreeDict API and properties."""

    def test_api(self):
        """Variant API test from lab requirements."""
        empty_d = empty()
        l1 = cons(None, "c", cons(2, "b", cons("a", 1, empty_d)))
        l2 = cons("a", 1, cons(None, "c", cons(2, "b", empty_d)))

        self.assertEqual(str(empty_d), "{}")
        self.assertIn(
            str(l1),
            [
                "{'a': 1, 2: 'b', None: 'c'}",
                "{'a': 1, None: 'c', 2: 'b'}",
                "{2: 'b', 'a': 1, None: 'c'}",
                "{2: 'b', None: 'c', 'a': 1}",
                "{None: 'c', 2: 'b', 'a': 1}",
                "{None: 'c', 'a': 1, 2: 'b'}",
            ],
        )
        self.assertNotEqual(empty_d, l1)
        self.assertNotEqual(empty_d, l2)
        self.assertEqual(l1, l2)

        self.assertEqual(length(empty_d), 0)
        self.assertEqual(length(l1), 3)
        self.assertEqual(length(l2), 3)

        self.assertIn(
            str(remove(l1, None)),
            ["{2: 'b', 'a': 1}", "{'a': 1, 2: 'b'}"],
        )
        self.assertIn(
            str(remove(l1, "a")),
            ["{2: 'b', None: 'c'}", "{None: 'c', 2: 'b'}"],
        )

        self.assertFalse(member(None, empty_d))
        self.assertTrue(member(None, l1))
        self.assertTrue(member("a", l1))
        self.assertTrue(member(2, l1))
        self.assertFalse(member(3, l1))

        self.assertIn(
            to_list(l1),
            map(
                list,
                itertools.permutations(
                    [("a", 1), (2, "b"), (None, "c")]
                ),
            ),
        )
        self.assertEqual(
            l1,
            from_list([("a", 1), (2, "b"), (None, "c")]),
        )
        self.assertEqual(
            l1,
            from_list([(2, "B"), ("a", 1), (2, "b"), (None, "c")]),
        )

        self.assertEqual(
            concat(l1, l2),
            from_list([(2, "B"), ("a", 1), (2, "b"), (None, "c")]),
        )

        buf = []
        for e in l1:
            buf.append(e)
        self.assertIn(
            buf,
            map(list, itertools.permutations(["a", 2, None])),
        )

        lst = list(
            map(lambda e: e[0], to_list(l1))
        ) + list(
            map(lambda e: e[0], to_list(l2))
        )
        for e in l1:
            lst.remove(e)
        for e in l2:
            lst.remove(e)
        self.assertEqual(lst, [])

    def test_map(self):
        """Test map_lst preserves structure and applies function."""
        d = from_list([("a", 1), ("b", 2)])
        mapped = map_lst(d, lambda k, v: v * 2)
        self.assertEqual(mapped, from_list([("a", 2), ("b", 4)]))
        self.assertEqual(d, from_list([("a", 1), ("b", 2)]))

    def test_filter(self):
        """Test filter_lst selects matching elements."""
        d = from_list([("a", 1), ("b", 2), ("c", 3)])
        filtered = filter_lst(d, lambda k, v: v > 1)
        self.assertEqual(
            filtered,
            from_list([("b", 2), ("c", 3)]),
        )

    def test_reduce(self):
        """Test reduce_lst aggregates values."""
        d = from_list([("a", 1), ("b", 2), ("c", 3)])
        total = reduce_lst(d, lambda acc, k, v: acc + v, 0)
        self.assertEqual(total, 6)

    def test_find(self):
        """Test find returns first matching pair or None."""
        d = from_list([("a", 1), ("b", 2)])
        self.assertEqual(
            find(d, lambda k, v: v == 2),
            ("b", 2),
        )
        self.assertIsNone(find(d, lambda k, v: v == 5))

    def test_iterator(self):
        """Test functional iterator yields keys in sorted order."""
        d = from_list([("b", 2), ("a", 1)])
        it = iterator(d)
        self.assertEqual(it(), "a")
        self.assertEqual(it(), "b")
        with self.assertRaises(StopIteration):
            it()

    def test_reverse(self):
        """Test reverse rebuilds tree; inorder stays sorted."""
        d = from_list([("c", 3), ("a", 1), ("b", 2)])
        rev = reverse(d)
        # BST inorder traversal is always sorted by key
        self.assertEqual(to_list(rev), to_list(d))
        # Result is a new object
        self.assertIsNot(rev, d)

    # ---------- Property-Based Tests ----------

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_from_list_to_list_equality(self, d):
        """to_list(from_list(items)) yields sorted items."""
        items = list(d.items())
        self.assertEqual(
            to_list(from_list(items)),
            sorted(items),
        )

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_monoid_identity(self, d):
        """empty() is left and right identity for concat."""
        a = from_list(list(d.items()))
        self.assertEqual(concat(empty(), a), a)
        self.assertEqual(concat(a, empty()), a)

    @given(
        st.dictionaries(st.integers(), st.integers()),
        st.dictionaries(st.integers(), st.integers()),
        st.dictionaries(st.integers(), st.integers()),
    )
    def test_monoid_associativity(self, d1, d2, d3):
        """concat is associative."""
        a = from_list(list(d1.items()))
        b = from_list(list(d2.items()))
        c = from_list(list(d3.items()))
        self.assertEqual(
            concat(concat(a, b), c),
            concat(a, concat(b, c)),
        )

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_immutability_after_cons(self, d):
        """Original dict is unchanged after cons."""
        items = list(d.items())
        a = from_list(items)
        old_repr = str(a)
        b = cons(999, "new", a)
        self.assertEqual(str(a), old_repr)
        self.assertTrue(member(999, b))
        self.assertFalse(member(999, a))

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_immutability_after_remove(self, d):
        """Original dict is unchanged after remove."""
        if not d:
            return
        items = list(d.items())
        a = from_list(items)
        old_repr = str(a)
        key_to_remove = items[0][0]

        b = remove(a, key_to_remove)
        self.assertEqual(str(a), old_repr)
        self.assertFalse(member(key_to_remove, b))
        self.assertTrue(member(key_to_remove, a))

    @given(st.lists(st.tuples(st.integers(), st.integers())))
    def test_override_behavior(self, lst):
        """Later values override earlier values for duplicate keys."""
        a = from_list(lst)
        expected_dict = {}
        for k, v in lst:
            expected_dict[k] = v
        self.assertEqual(
            a,
            from_list(list(expected_dict.items())),
        )

    @given(st.dictionaries(
        st.one_of(
            st.none(),
            st.integers(),
            st.sampled_from(["x", "y", "z"]),
        ),
        st.integers(),
    ))
    def test_mixed_keys_roundtrip(self, d):
        """Heterogeneous keys are ordered by type rank."""
        items = list(d.items())
        result = to_list(from_list(items))

        def _sort_key(t):
            k = t[0]
            if k is None:
                return (0, k)
            if isinstance(k, (int, float)):
                return (1, k)
            if isinstance(k, str):
                return (2, k)
            return (3, k)

        self.assertEqual(result, sorted(items, key=_sort_key))


if __name__ == "__main__":
    unittest.main()
