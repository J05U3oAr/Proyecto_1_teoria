import tempfile
import unittest
from pathlib import Path

from automata import AutomatonSimulator, DFAMinimizer, SubsetConstructor, ThompsonBuilder
from io_ import RegexFileReader
from pipeline import LexicalAnalyzerPipeline
from regex import EPSILON, RegexTokenizer, ShuntingYard


def build(regex: str):
    postfix = ShuntingYard().to_postfix(RegexTokenizer().tokenize(regex))
    nfa = ThompsonBuilder().build(postfix)
    dfa = SubsetConstructor().convert(nfa)
    return nfa, dfa, DFAMinimizer().minimize(dfa)


class ProjectRequirementsTests(unittest.TestCase):
    def test_epsilon_is_backslash_tilde(self):
        self.assertEqual(EPSILON, r"\~")
        tokens = RegexTokenizer().tokenize(r"(a|\~)b*")
        self.assertIn(r"\~", tokens)
        nfa, dfa, minimized = build(r"(a|\~)b*")
        simulator = AutomatonSimulator()
        for word in ("", "a", "b", "abbb"):
            self.assertTrue(simulator.simulate_nfa(nfa, word))
            self.assertTrue(simulator.simulate_dfa(dfa, word))
            self.assertTrue(simulator.simulate_dfa(minimized, word))

    def test_escaped_operator_is_a_literal(self):
        nfa, dfa, minimized = build(r"\*a")
        simulator = AutomatonSimulator()
        for automaton, simulate in (
            (nfa, simulator.simulate_nfa),
            (dfa, simulator.simulate_dfa),
            (minimized, simulator.simulate_dfa),
        ):
            self.assertTrue(simulate(automaton, "*a"))
            self.assertFalse(simulate(automaton, "a"))

    def test_character_classes_and_ranges(self):
        nfa, dfa, minimized = build(r"[a-cA-C0-2.\]]+")
        simulator = AutomatonSimulator()
        for automaton, simulate in (
            (nfa, simulator.simulate_nfa),
            (dfa, simulator.simulate_dfa),
            (minimized, simulator.simulate_dfa),
        ):
            self.assertTrue(simulate(automaton, "aB2.]"))
            self.assertFalse(simulate(automaton, "d"))

    def test_url_examples(self):
        regex = (
            r"https?://[a-zA-Z0-9.-]+"
            r"(/[a-zA-Z0-9.~:/?#[\]@!$&'()+,;=-]*)?"
            r"(\?[a-zA-Z0-9.~:/?#[\]@!$&'()+,;=-]*)?"
        )
        nfa, dfa, minimized = build(regex)
        simulator = AutomatonSimulator()
        examples = {
            "https://www.youtube.com/": True,
            "https://api.site.com/users?limit=10&offset=0": True,
            "https://www.youtube@.com/": False,
        }
        for word, expected in examples.items():
            self.assertEqual(simulator.simulate_nfa(nfa, word), expected)
            self.assertEqual(simulator.simulate_dfa(dfa, word), expected)
            self.assertEqual(simulator.simulate_dfa(minimized, word), expected)

    def test_automata_agree_on_acceptance(self):
        nfa, dfa, minimized = build(r"(a|b)*abb(a|b)*")
        simulator = AutomatonSimulator()
        for word, expected in {
            "": False, "abb": True, "aabb": True, "babbab": True, "ab": False,
        }.items():
            self.assertEqual(simulator.simulate_nfa(nfa, word), expected)
            self.assertEqual(simulator.simulate_dfa(dfa, word), expected)
            self.assertEqual(simulator.simulate_dfa(minimized, word), expected)

    def test_each_nfa_starts_at_q0(self):
        first, _, _ = build("ab")
        second, _, _ = build("(a|b)*")
        self.assertEqual(first.start.label, "q0")
        self.assertEqual(second.start.label, "q0")

    def test_pipeline_renders_three_automata(self):
        with tempfile.TemporaryDirectory() as directory:
            result = LexicalAnalyzerPipeline().analyze(r"a\~b", "ab", directory)
            self.assertTrue(result.nfa_accepts)
            self.assertEqual(len(result.images), 3)
            self.assertTrue(all(image.exists() and image.suffix == ".png" for image in result.images))

    def test_reader_processes_one_regex_per_line(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "regexes.txt"
            source.write_text("a\n\n(a|b)*\n", encoding="utf-8")
            self.assertEqual(RegexFileReader().read(source), ["a", "(a|b)*"])


if __name__ == "__main__":
    unittest.main()
