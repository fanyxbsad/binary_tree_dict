# GROUP- 6 - lab 2 - variant 6

This project demonstrates an immutable Dictionary based on a Binary
Search Tree (BST). It adheres to a functional programming paradigm,
utilizing purely recursive algorithms and structural sharing to avoid
unnecessary data copying.

## Project structure

- `binary_tree_dict.py` -- implementation of the immutable binary
  tree dictionary with a functional-style API.
- `test_binary_tree_dict.py` -- unit and Property-Based Tests
  (PBT) for the dictionary.

## Features

- PBT: `test_monoid_associativity`
- PBT: `test_immutability_after_cons`
- PBT: `test_immutability_after_remove`
- Heterogeneous key support (`None`, `int`, `str` mixed safely).

## Contribution

- Fan Yuxin (2568823977@qq.com) -- all work.

## Changelog

- 11.05.2026 - 2
- Add property-based tests for monoid laws and immutability.
- 10.05.2026 - 1
- Implement functional API (`cons`, `remove`, `map`, etc.).
- 10.05.2026 - 0
- Initial project structure setup.

## Design notes

- **Immutability & Structural Sharing**: Interaction with the
  structure never mutates it. Methods like `cons` or `remove`
  construct and return new tree instances. Unchanged subtrees are
  directly linked (shared) to optimize memory usage.

- **Pure Recursion**: The implementation strictly avoids `for` and
  `while` loops. All traversals, mappings, and reductions are
  achieved through recursion. Tail recursion is explicitly applied
  in functions like `from_list` and `concat` to prevent stack
  overflows on larger datasets.

- **Heterogeneous Key Comparison**: Python 3 natively raises a
  `TypeError` when comparing different types (e.g., `None < 1`).
  To pass tests with mixed-type keys, a `_key_rank` utility maps
  types to integer priorities, ensuring safe and deterministic
  BST ordering.

- **Monoid Interface**: The structure acts as a monoid with
  `empty()` as the identity element and `concat()` as the binary
  operation. Property tests verify both left/right identity and
  associativity laws.
