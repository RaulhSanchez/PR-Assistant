import pytest
from autoreadme.differ import analyze_changes

def test_analyze_changes_breaking():
    old = "def foo(a, b):\n    return a + b"
    new = "def foo(a, b, c):\n    return a + b + c"
    report = analyze_changes("test.py", old, new)
    assert report.is_breaking
    assert len(report.signature_changes) == 1
    assert "foo" in report.signature_changes[0]

def test_analyze_changes_no_breaking():
    old = "def foo(a, b):\n    return a + b"
    new = "def foo(a, b):\n    print('hello')\n    return a + b"
    report = analyze_changes("test.py", old, new)
    assert not report.is_breaking
    assert len(report.signature_changes) == 0

def test_analyze_changes_added_removed():
    old = "def foo(): pass"
    new = "def bar(): pass"
    report = analyze_changes("test.py", old, new)
    assert report.added_functions == ["bar"]
    assert report.removed_functions == ["foo"]
    assert report.is_breaking # Removing a function is breaking
