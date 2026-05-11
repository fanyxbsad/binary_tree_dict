from functools import reduce
from typing import (
    Callable,
    Any,
    List,
    Tuple,
    Iterator as IterType,
    Optional
)


def _key_rank(k: Any) -> int:
    """Assign comparison priority for heterogeneous types."""
    if k is None:
        return 0
    if isinstance(k, (int, float)):
        return 1
    if isinstance(k, str):
        return 2
    return 3


def _lt(k1: Any, k2: Any) -> bool:
    """Safe less-than comparison function."""
    if k1 == k2:
        return False
    r1, r2 = _key_rank(k1), _key_rank(k2)
    if r1 != r2:
        return r1 < r2
    return k1 < k2


class _Node:
    """Internal immutable binary search tree node."""
    __slots__ = ('key', 'value', 'left', 'right')

    def __init__(
        self,
        key: Any,
        value: Any,
        left: Optional['_Node'] = None,
        right: Optional['_Node'] = None
    ):
        self.key = key
        self.value = value
        self.left = left
        self.right = right


class BinaryTreeDict:
    """External representation of immutable binary tree dict."""

    def __init__(self, root: Optional[_Node] = None):
        self._root = root

    def __str__(self) -> str:
        pairs = [f"{k!r}: {v!r}" for k, v in to_list(self)]
        return "{" + ", ".join(pairs) + "}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinaryTreeDict):
            return False

        def _safe_sort_key(item):
            k, v = item
            return (_key_rank(k), k)

        return sorted(
            to_list(self), key=_safe_sort_key
        ) == sorted(
            to_list(other), key=_safe_sort_key
        )

    def __iter__(self) -> IterType[Any]:
        return _inorder_gen(self._root)


def _inorder_gen(node: Optional[_Node]) -> IterType[Any]:
    """Recursive inorder generator, yields keys only."""
    if node is None:
        return
    yield from _inorder_gen(node.left)
    yield node.key
    yield from _inorder_gen(node.right)


def _remove_min(
    node: Optional[_Node]
) -> Tuple[Any, Any, Optional[_Node]]:
    """Find and remove the minimum node in subtree."""
    if node is None:
        raise ValueError("Node cannot be None")
    if node.left is None:
        return node.key, node.value, node.right
    mk, mv, new_left = _remove_min(node.left)
    if new_left is node.left:
        return mk, mv, node
    return mk, mv, _Node(node.key, node.value, new_left, node.right)


def empty() -> BinaryTreeDict:
    """Monoid identity element."""
    return BinaryTreeDict()


def cons(
    key: Any,
    value: Any,
    d: BinaryTreeDict
) -> BinaryTreeDict:
    """Recursively insert/update key-value, returns new dict."""
    def _insert(node: Optional[_Node]) -> Optional[_Node]:
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


def member(key: Any, d: BinaryTreeDict) -> bool:
    """Recursively check if key exists."""
    def _mem(node: Optional[_Node]) -> bool:
        if node is None:
            return False
        if key == node.key:
            return True
        if _lt(key, node.key):
            return _mem(node.left)
        return _mem(node.right)
    return _mem(d._root)


def remove(
    d: BinaryTreeDict,
    key: Any
) -> BinaryTreeDict:
    """Recursively remove key, returns new dict."""
    def _del(node: Optional[_Node]) -> Optional[_Node]:
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


def length(d: BinaryTreeDict) -> int:
    """Recursively calculate dict size."""
    def _len(node: Optional[_Node]) -> int:
        if node is None:
            return 0
        return 1 + _len(node.left) + _len(node.right)
    return _len(d._root)


def to_list(d: BinaryTreeDict) -> List[Tuple[Any, Any]]:
    """Recursively convert to Python list via inorder traversal."""
    res = []

    def _builder(node: Optional[_Node]):
        if node is None:
            return
        _builder(node.left)
        res.append((node.key, node.value))
        _builder(node.right)

    _builder(d._root)
    return res


def from_list(lst: List[Tuple[Any, Any]]) -> BinaryTreeDict:
    """Tail-recursively build dict from Python list."""
    def _from(idx: int, acc: BinaryTreeDict) -> BinaryTreeDict:
        if idx == len(lst):
            return acc
        k, v = lst[idx]
        return _from(idx + 1, cons(k, v, acc))

    return _from(0, empty())


def concat(
    d1: BinaryTreeDict,
    d2: BinaryTreeDict
) -> BinaryTreeDict:
    """Monoid concatenation, merges d2 into d1."""
    lst2 = to_list(d2)

    def _concat(idx: int, acc: BinaryTreeDict) -> BinaryTreeDict:
        if idx == len(lst2):
            return acc
        k, v = lst2[idx]
        return _concat(idx + 1, cons(k, v, acc))

    return _concat(0, d1)


def reverse(d: BinaryTreeDict) -> BinaryTreeDict:
    """Reverse to_list sequence and rebuild dict."""
    def _reverse_list(lst: List, acc: List) -> List:
        if not lst:
            return acc
        return _reverse_list(lst[1:], [lst[0]] + acc)

    return from_list(_reverse_list(to_list(d), []))


def find(
    d: BinaryTreeDict,
    predicate: Callable[[Any, Any], bool]
) -> Optional[Tuple[Any, Any]]:
    """Recursively find first pair matching predicate."""
    def _find(node: Optional[_Node]):
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
    d: BinaryTreeDict,
    predicate: Callable[[Any, Any], bool]
) -> BinaryTreeDict:
    """Higher-order function filter."""
    return from_list(
        list(filter(lambda t: predicate(t[0], t[1]), to_list(d)))
    )


def map_lst(
    d: BinaryTreeDict,
    func: Callable[[Any, Any], Any]
) -> BinaryTreeDict:
    """Higher-order function map."""
    return from_list(
        list(
            map(lambda t: (t[0], func(t[0], t[1])), to_list(d))
        )
    )


def reduce_lst(
    d: BinaryTreeDict,
    func: Callable[[Any, Any, Any], Any],
    initial: Any
) -> Any:
    """Higher-order function reduce."""
    return reduce(
        lambda acc, t: func(acc, t[0], t[1]), to_list(d), initial
    )


def iterator(d: BinaryTreeDict) -> Callable[[], Any]:
    """Closure-style functional iterator."""
    gen = _inorder_gen(d._root)

    def foo():
        return next(gen)

    return foo
