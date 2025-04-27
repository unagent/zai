
from zai.user_prompts import *
import pytest

def test_apply_matches():
    text = "Hello, world!"
    matches = [lambda: 0, lambda: 7]
    replacements = ["Goodbye", "earth"]
    result = apply_matches(text, matches, replacements)
    assert result == "Goodbye, earth!"

def test_apply_matches_empty():
    text = "Hello, world!"
    matches = []
    replacements = []
    result = apply_matches(text, matches, replacements)
    assert result == text

def test_apply_matches_mismatched():
    text = "Hello, world!"
    matches = [lambda: 0, lambda: 7]
    replacements = ["Goodbye"]
    with pytest.raises(ValueError):
        apply_matches(text, matches, replacements)

# ai! write tests for apply_matches function from user_prompts
