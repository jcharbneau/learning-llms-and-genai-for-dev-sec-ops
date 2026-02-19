from __future__ import annotations

import unittest

from scripts.check_curriculum_contract import validate


class TestCurriculumContract(unittest.TestCase):
    def test_curriculum_contract(self) -> None:
        errors = validate()
        if errors:
            self.fail("\n" + "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
