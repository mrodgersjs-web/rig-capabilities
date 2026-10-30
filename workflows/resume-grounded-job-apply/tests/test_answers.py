import copy
import hashlib
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("check_answers", Path(__file__).parents[1] / "scripts/check_answers.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AnswerGateTests(unittest.TestCase):
    def setUp(self):
        self.resume = b"Synthetic employment: Example Employer."
        digest = hashlib.sha256(self.resume).hexdigest()
        self.facts = {"source_sha256": digest, "employers": [{"id": "example", "name": "Example Employer", "aliases": ["Former Example"]}]}
        self.packet = {"resume_sha256": digest, "job_url": "https://careers.example.test/123", "answers": [{"question": "Were you employed by Example Employer?", "kind": "prior_employer", "employer": "Example Employer", "answer": "Yes", "source": "resume:employer:example", "required": True}]}

    def test_resume_employer_yes(self):
        self.assertEqual(module.check(self.resume, self.facts, self.packet), [])

    def test_explicit_alias(self):
        self.packet['answers'][0]['employer'] = 'Former Example'
        self.assertEqual(module.check(self.resume, self.facts, self.packet), [])

    def test_unlisted_employer_yes_is_rejected(self):
        self.packet['answers'][0]['employer'] = 'Client Corporation'
        self.assertTrue(module.check(self.resume, self.facts, self.packet))

    def test_unlisted_employer_no(self):
        self.packet['answers'][0].update(employer='Client Corporation', answer='No', source='standing_user_rule:resume_employment_only')
        self.assertEqual(module.check(self.resume, self.facts, self.packet), [])

    def test_blanket_no_for_known_employer_rejected(self):
        self.packet['answers'][0].update(answer='No', source='standing_user_rule:resume_employment_only')
        self.assertTrue(module.check(self.resume, self.facts, self.packet))

    def test_employer_substring_does_not_match(self):
        self.packet['answers'][0]['employer'] = 'Example Employer Partner'
        self.assertTrue(module.check(self.resume, self.facts, self.packet))

    def test_changed_resume_rejected(self):
        self.assertTrue(module.check(self.resume + b'changed', self.facts, self.packet))

    def test_required_unknown_rejected(self):
        self.packet['answers'][0].update(kind='other', answer=None, source=None)
        self.assertTrue(module.check(self.resume, self.facts, self.packet))

    def test_optional_unanswered_allowed(self):
        self.packet['answers'][0].update(kind='other', answer=None, source=None, required=False)
        self.assertEqual(module.check(self.resume, self.facts, self.packet), [])

    def test_no_does_not_infer_eligibility(self):
        self.packet['answers'][0].update(kind='other', answer='No', source='standing_user_rule:resume_employment_only')
        self.assertTrue(module.check(self.resume, self.facts, self.packet))

    def test_explicit_user_answer(self):
        self.packet['answers'][0].update(kind='other', answer='No', source='user-confirmed:exact-question-2026-09-07')
        self.assertEqual(module.check(self.resume, self.facts, self.packet), [])

    def test_empty_packet_and_baseline_fail(self):
        self.packet['answers'] = []
        self.assertTrue(module.check(self.resume, self.facts, self.packet))
        facts = copy.deepcopy(self.facts)
        facts['employers'] = []
        self.assertTrue(module.check(self.resume, facts, self.packet))


if __name__ == '__main__':
    unittest.main()
