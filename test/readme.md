# Important

When running all the tests using pytest, the console test must run first; 
since pytest runs tests in alphabetical order, this is why it is named test_a_console.py

# About these tests

For simplicity, wherever possible, I follow [pytest](https://docs.pytest.org/en/latest/contents.html)'s strategy of simply using Python's `assert` statements and naming test files and test functions within these files all starting with `test_` for easy discovery. `pytest` is not part of Python's standard library and you may have to intall it. 

However, since `pyextensions` changes the way `import` works, the _normal_ approach used by `pytest` is modified.  For each test, two files are created:

    test_X.py
    X_testfile.py

`X_testfile.py` [_see below for the naming convention_] is the actual file that contains the tests for the experimental, and almost always invalid Python syntax.  As such, it cannot be imported by the normal mechanism.  `test_X.py` imports `experimental`, which install an import hook. It then imports `X_testfile.py` which can be processed by the `experimental` import hook.

`X_testfile.py`'s content should be something like:

```python
from __experimental__ import X_feature

def test_one():
    ...
    assert something, "something is tested"
    ...

def test_another():
    ...
    assert something_else, "something else is tested"
    ...

if __name__ == "__main__":
    test_one()
    test_another()
    print("Success.")
```

To ensure that the development version of `pyextensions` is used, `test_X.py` will first import a file (`common.py`) which changes `sys.path` to ensure that this is the case.

### About the naming convention

Suppose I define a transformation named `X` found in file `X.py`. When creating test files in the `test` directory, it is important not to have any file named `X.py` as well.  Furthermore, pytest automatically loads files named `test_X.py` _and_ apparently also `X_test.py`.  For this reason, if I need a file imported by `test_X.py`, I will often most often name it `X_testfile.py` so as to avoid any confusion.

## Problem with output capture

When output needs to be captured, for example for tests performed with the transformation that enables the use of `print` as a keyword instead, the method used by pytest for capturing the output does not work as pytest will try to get the source of the file with modified, and thus invalid python syntax and execute it bypassing any transformations performed by `pyextensions`.  In those cases, one must do the capture using a custom approach. An example of this can be seen in the file `print_keyword_test.py`.

## Using only pytest

To write a series of tests that can be discovered by `pytest`, a file named `test_X` has only to contain one line:

    from .X_testfile import *

To run all tests from the parent directory containing the `test` folder, the following can be used:

    python -m pytest

or perhaps more simply:

    pytest


## Running a single test without pytest

To run a single test file `X_testfile.py` without using pytest, we simply have to do

    python -m pyextensions test.X_testfile

also from the parent directory
