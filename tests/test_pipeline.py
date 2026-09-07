"""
Pruebas básicas del pipeline completo. Ejecutar con:
    pytest tests/
desde la raíz del proyecto (o `python -m pytest` si el import falla,
para que la raíz del proyecto quede en sys.path).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import shutil
import tempfile

import pytest

from pipeline import LexicalAnalyzerPipeline
from io_.file_reader import RegexFileReader


@pytest.fixture()
def pipeline():
    tmp_dir = tempfile.mkdtemp()
    yield LexicalAnalyzerPipeline(output_dir=tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)


CASES = [
    # (regex, cadena, esperado)
    ("(b|b)*abb(a|b)*", "babbaaaa", True),
    ("(b|b)*abb(a|b)*", "aaaa", False),
    ("(b|b)*abb(a|b)*", "abb", True),
    ("a(b|c)*d", "ad", True),
    ("a(b|c)*d", "abcbccd", True),
    ("a(b|c)*d", "abcbccx", False),
    ("(ab)+", "ababab", True),
    ("(ab)+", "", False),
    ("(ab)+", "aba", False),
    ("colou?r", "color", True),
    ("colou?r", "colour", True),
    ("colou?r", "colouur", False),
    ("~", "", True),
    ("~", "~", False),
    ("(a|~)b*", "", True),
    ("(a|~)b*", "abbb", True),
    ("a~b", "ab", True),
    ("a~b", "a~b", False),
    ("ε", "ε", True),
    ("ε", "", False),
    (r"\*", "*", True),
    (r"\*", "", False),
    (r"a\|b", "a|b", True),
    (r"\(\)", "()", True),
    (r"a\.b", "a.b", True),
]


@pytest.mark.parametrize("regex,w,expected", CASES)
def test_nfa_dfa_min_dfa_agree_with_expected(pipeline, regex, w, expected):
    result = pipeline.process(regex, w)
    assert result.nfa_accepts == expected
    assert result.dfa_accepts == expected
    assert result.min_dfa_accepts == expected


def test_minimizer_does_not_increase_state_count(pipeline):
    result = pipeline.process("(b|b)*abb(a|b)*", "babbaaaa")
    assert len(result.min_dfa.states) <= len(result.dfa.states)


def test_images_are_generated(pipeline):
    result = pipeline.process("a(b|c)*d", "abccd")
    for image_path in (result.nfa_image, result.dfa_image, result.min_dfa_image):
        assert Path(image_path).exists()


def test_file_reader_loads_regexes_and_strings(tmp_path):
    regex_file = tmp_path / "regexes.txt"
    strings_file = tmp_path / "strings.txt"
    regex_file.write_text("a*\n\n(ab)+\n", encoding="utf-8")
    strings_file.write_text("aaa\n\nabab\n", encoding="utf-8")

    reader = RegexFileReader()

    assert reader.read_regexes(str(regex_file)) == ["a*", "(ab)+"]
    assert reader.read_strings(str(strings_file)) == ["aaa", "", "abab"]
