# Change Log

## [2.1.0] - 2025-08-17

Changes:

- Camelize would capitalize words starting with an underscore. It now leaves them unchanged.

  - Old: `"_special"` -> `"Special"`
  - Now: `"_special"` -> `"_special"`

- Improve test coverage
- Update README

## [2.0.0] - 2025-07-16

Breaking changes:

- The API error response now **always** includes the keys: `title`, `detail`, and `invalid_param`. The `title` key is always populated, while `detail` and `invalid_param` may be `null` depending on the error source.
- Drop support for python 3.8

Changes:

- Improve code modularity and readability
- Split tests in unittest and integration tests
- Improve test coverage
- Update Makefile
- Update README

## [1.0.3] - 2025-03-16

Changes:

- Fix DRF API settings initialization
- Improve tests
- Update README

## [1.0.2] - 2024-09-08

Changes:

- Add docstrings
- Improve Makefile
- Improve README

## [1.0.1] - 2024-04-30

Changes:

- Upgrade dependencies

## [1.0.0] - 2024-04-26

Changes:

- First release on PyPI
