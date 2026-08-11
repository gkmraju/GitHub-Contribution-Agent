import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from github_contribution_agent.execution import PublicationEvidence, validate_publication


class PublicationPolicyTests(unittest.TestCase):
    def test_accepts_recorded_successful_validation_for_draft(self):
        command = "python -m unittest discover -s tests -v"
        evidence = PublicationEvidence(
            validation_commands=(command,),
            successful_commands=(command,),
            claims_tests_passed=True,
        )

        self.assertEqual(validate_publication(evidence), ())

    def test_blocks_unsupported_test_claim(self):
        evidence = PublicationEvidence(
            validation_commands=("python -m unittest",),
            claims_tests_passed=True,
        )

        self.assertTrue(validate_publication(evidence))

    def test_blocks_legal_and_personal_representations(self):
        evidence = PublicationEvidence(
            accepts_legal_attestation=True,
            makes_personal_representation=True,
        )

        violations = validate_publication(evidence)
        self.assertEqual(len(violations), 2)

    def test_requires_draft_pull_request(self):
        self.assertIn(
            "pull request must be opened as a draft",
            validate_publication(PublicationEvidence(pull_request_is_draft=False)),
        )


if __name__ == "__main__":
    unittest.main()
