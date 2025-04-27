
from zai.user_prompts import *
import pytest

def test_apply_matches():
    text = "Hello, <tag> world!"
    matches = list(re.finditer(r'<tag>', text))
    replacements = ["beautiful"]
    result = apply_matches(text, matches, replacements)
    assert result == "Hello, beautiful world!"

def test_apply_matches_empty():
    text = "Hello, <tag> world!"
    matches = list(re.finditer(r'<tag>', text))
    replacements = []
    with pytest.raises(ValueError):
        apply_matches(text, matches, replacements)

def test_apply_matches_mismatched():
    text = "Hello, <tag> world! <tag2>"
    matches = list(re.finditer(r'<tag>', text))
    replacements = ["beautiful"]
    with pytest.raises(ValueError):
        apply_matches(text, matches, replacements)

def test_apply_matches_multiple():
    text = "Hello, <tag> world! <tag2>"
    matches = list(re.finditer(r'<tag|tag2>', text))
    replacements = ["beautiful", "earth"]
    result = apply_matches(text, matches, replacements)
    assert result == "Hello, beautiful world! earth"
