"""Immutable dictionary implementation based on binary search tree."""

from __future__ import annotations

from functools import reduce
from typing import (
    Any,
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
)

K = TypeVar("K")
V = TypeVar("V")
V2 = TypeVar("V2")
A = TypeVar("A")


def _key_rank(k: Any) -> int:
    """Return comparison priority for heterogeneous types."""
    if k is None:
        return 0
    if isinstance(k, (int, float)):
        return 1
    if isinstance(k, str):
        return 2
    return 3


def _lt(k1: Any, k2: Any) -> bool:
    """Safe less-than comparison for heterogeneous keys."""
    if k1 == k2:
        return False
    r1, r2 = _key_rank(k1), _key_rank(k2)
    if r1 != r2:
        return r1 < r2
    return k1 < k2


class _Node(Generic[K, V]):
    """Internal immutable binary search tree node."""

    __slots__ = ("key", "value", "left", "right")

    def __init__(
        self,
        key: K,
        value: V,
        left: Optional[_Node[K, V]] = None,
        right: Optional[_Node[K, V]] = None,
    ) -> None:
        self.key = key
        self.value = value
        self.left = left
        self.right = right


class BinaryTreeDict(Generic[K, V]):
    """External representation of immutable binary tree dictionary."""

    def __init__(self, root: Optional[_Node[K, V]] = None) -> None:
        self._root = root

    def __str__(self) -> str:
        pairs = [f"{k!r}: {v!r}" for k, v in to_list(self)]
        return "{" + ", ".join(pairs) + "}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinaryTreeDict):
            return False
        return to_list(self) == to_list(other)

    def __iter__(self) -> Iterator[K]:
        return _inorder_gen(self._root)


def _inorder_gen(node: Optional[_Node[K, V]]) -> Iterator[K]:
    """Yield keys in ascending order."""
    if node is None:
        return
    yield from _inorder_gen(node.left)
    yield node.key
    yield from _inorder_gen(node.right)


def _remove_min(
    node: _Node[K, V],
) -> Tuple[K, V, Optional[_Node[K, V]]]:
    """Find and remove the minimum node in subtree."""
    if node is None:
        raise ValueError("Node cannot be None")
    if node.left is None:
        return node.key, node.value, node.right
    mk, mv, new_left = _remove_min(node.left)
    if new_left is node.left:
        return mk, mv, node
    return mk, mv, _Node(
        node.key, node.value, new_left, node.right
    )


def empty() -> BinaryTreeDict[K, V]:
    """Return the monoid identity element."""
    return BinaryTreeDict()


def cons(
    key: K,
    value: V,
    d: BinaryTreeDict[K, V],
) -> BinaryTreeDict[K, V]:
    """Insert or update key-value pair, returning a new dictionary."""

    def _insert(node: Optional[_Node[K, V]]) -> Optional[_Node[K, V]]:
        if node is None:
            return _Node(key, value)
        if key == node.key:
            if value == node.value:
                return node
            return _Node(key, value, node.left, node.right)
        if _lt(key, node.key):
            new_left = _insert(node.left)
            if new_left is node.left:
                return node
            return _Node(
                node.key, node.value, new_left, node.right
            )
        else:
            new_right = _insert(node.right)
            if new_right is node.right:
                return node
            return _Node(
                node.key, node.value, node.left, new_right
            )

    return BinaryTreeDict(_insert(d._root))


def member(key: K, d: BinaryTreeDict[K, V]) -> bool:
    """Check if key exists in dictionary."""

    def _mem(node: Optional[_Node[K, V]]) -> bool:
        if node is None:
            return False
        if key == node.key:
            return True
        if _lt(key, node.key):
            return _mem(node.left)
        return _mem(node.right)

    return _mem(d._root)


def remove(
    d: BinaryTreeDict[K, V],
    key: K,
) -> BinaryTreeDict[K, V]:
    """Remove key from dictionary, returning a new dictionary."""

    def _del(node: Optional[_Node[K, V]]) -> Optional[_Node[K, V]]:
        if node is None:
            return None
        if _lt(key, node.key):
            new_left = _del(node.left)
            if new_left is node.left:
                return node
            return _Node(
                node.key, node.value, new_left, node.right
            )
        if _lt(node.key, key):
            new_right = _del(node.right)
            if new_right is node.right:
                return node
            return _Node(
                node.key, node.value, node.left, new_right
            )

        if node.left is None:
            return node.right
        if node.right is None:
            return node.left

        mk, mv, new_right = _remove_min(node.right)
        return _Node(mk, mv, node.left, new_right)

    return BinaryTreeDict(_del(d._root))


def length(d: BinaryTreeDict[K, V]) -> int:
    """Return the number of key-value pairs."""

    def _len(node: Optional[_Node[K, V]]) -> int:
        if node is None:
            return 0
        return 1 + _len(node.left) + _len(node.right)

    return _len(d._root)


def to_list(d: BinaryTreeDict[K, V]) -> List[Tuple[K, V]]:
    """Convert dictionary to Python list via inorder traversal."""
    res: List[Tuple[K, V]] = []

    def _builder(node: Optional[_Node[K, V]]) -> None:
        if node is None:
            return
        _builder(node.left)
        res.append((node.key, node.value))
        _builder(node.right)

    _builder(d._root)
    return res


def from_list(lst: List[Tuple[K, V]]) -> BinaryTreeDict[K, V]:
    """Build dictionary from Python list."""

    def _from(
        idx: int, acc: BinaryTreeDict[K, V]
    ) -> BinaryTreeDict[K, V]:
        if idx == len(lst):
            return acc
        k, v = lst[idx]
        return _from(idx + 1, cons(k, v, acc))

    return _from(0, empty())


def concat(
    d1: BinaryTreeDict[K, V],
    d2: BinaryTreeDict[K, V],
) -> BinaryTreeDict[K, V]:
    """Monoid concatenation: merge d2 into d1."""
    lst2 = to_list(d2)

    def _concat(
        idx: int, acc: BinaryTreeDict[K, V]
    ) -> BinaryTreeDict[K, V]:
        if idx == len(lst2):
            return acc
        k, v = lst2[idx]
        return _concat(idx + 1, cons(k, v, acc))

    return _concat(0, d1)


def reverse(d: BinaryTreeDict[K, V]) -> BinaryTreeDict[K, V]:
    """Reverse to_list sequence and rebuild dictionary.

    Note: for BST, inorder traversal is always sorted by key,
    so reverse + rebuild yields a different tree structure
    but the same inorder sequence.
    """

    def _reverse_list(
        lst: List[Tuple[K, V]], acc: List[Tuple[K, V]]
    ) -> List[Tuple[K, V]]:
        if not lst:
            return acc
        return _reverse_list(lst[1:], [lst[0]] + acc)

    return from_list(_reverse_list(to_list(d), []))


def find(
    d: BinaryTreeDict[K, V],
    predicate: Callable[[K, V], bool],
) -> Optional[Tuple[K, V]]:
    """Find first key-value pair matching predicate."""

    def _find(
        node: Optional[_Node[K, V]]
    ) -> Optional[Tuple[K, V]]:
        if node is None:
            return None
        left_res = _find(node.left)
        if left_res is not None:
            return left_res
        if predicate(node.key, node.value):
            return (node.key, node.value)
        return _find(node.right)

    return _find(d._root)


def filter_lst(
    d: BinaryTreeDict[K, V],
    predicate: Callable[[K, V], bool],
) -> BinaryTreeDict[K, V]:
    """Filter dictionary by predicate."""
    return from_list(
        list(filter(lambda t: predicate(t[0], t[1]), to_list(d)))
    )


def map_lst(
    d: BinaryTreeDict[K, V],
    func: Callable[[K, V], V2],
) -> BinaryTreeDict[K, V2]:
    """Map function over dictionary values."""
    return from_list(
        list(
            map(lambda t: (t[0], func(t[0], t[1])), to_list(d))
        )
    )


def reduce_lst(
    d: BinaryTreeDict[K, V],
    func: Callable[[A, K, V], A],
    initial: A,
) -> A:
    """Reduce dictionary to a single value."""
    return reduce(
        lambda acc, t: func(acc, t[0], t[1]), to_list(d), initial
    )


def iterator(d: BinaryTreeDict[K, V]) -> Callable[[], K]:
    """Return a closure-style functional iterator over keys."""
    gen = _inorder_gen(d._root)

    def _next() -> K:
        return next(gen)

    return _next
