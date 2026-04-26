import pytest

from core.config import settings
from services.mastery_service import MasteryService


class TestMasteryScoreFormula:
    def test_correct_increases_score(self):
        new = MasteryService.compute_new_score(0.3, "correct")
        assert new == pytest.approx(0.3 + settings.MASTERY_SCORE_INCREMENT)

    def test_incorrect_decreases_score(self):
        new = MasteryService.compute_new_score(0.6, "incorrect")
        assert new == pytest.approx(0.6 - settings.MASTERY_SCORE_DECREMENT)

    def test_score_never_exceeds_1(self):
        new = MasteryService.compute_new_score(0.99, "correct")
        assert new <= 1.0

    def test_score_never_below_0(self):
        new = MasteryService.compute_new_score(0.01, "incorrect")
        assert new >= 0.0

    def test_partial_gets_half_increment(self):
        new = MasteryService.compute_new_score(0.5, "partial")
        expected = 0.5 + settings.MASTERY_SCORE_INCREMENT * 0.5
        assert new == pytest.approx(expected)


class TestMasteryStatus:
    def test_mastered_at_threshold(self):
        status = MasteryService.compute_status(settings.MASTERY_CERT_THRESHOLD, 0)
        assert status == "mastered"

    def test_struggling_below_0_4_with_3_failures(self):
        status = MasteryService.compute_status(0.3, 3)
        assert status == "struggling"

    def test_attempted_between_0_2_and_0_4(self):
        status = MasteryService.compute_status(0.3, 0)
        assert status == "attempted"

    def test_encountered_below_0_2(self):
        status = MasteryService.compute_status(0.1, 0)
        assert status == "encountered"
