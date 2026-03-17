"""Tests for note generators."""

import pytest

from sessionnotes.generator.birp import BIRPNoteGenerator
from sessionnotes.generator.dap import DAPNoteGenerator
from sessionnotes.generator.soap import SOAPNoteGenerator
from sessionnotes.models import Session


@pytest.fixture
def anxiety_session() -> Session:
    return Session(
        session_id="S001",
        client_id="C001",
        session_number=3,
        duration_minutes=50,
        transcript=(
            "Client reported feeling increasingly anxious over the past week. "
            "I feel like I can't breathe sometimes and my heart races. "
            "I'm worried about losing my job. I've been having panic attacks "
            "at work. I tried the breathing exercises we discussed last time "
            "and they helped a little. I feel hopeful that therapy can help."
        ),
        modality="individual",
        presenting_concerns=["generalized anxiety", "panic attacks"],
    )


@pytest.fixture
def depression_session() -> Session:
    return Session(
        session_id="S002",
        client_id="C001",
        session_number=4,
        duration_minutes=50,
        transcript=(
            "Client appeared tearful and fatigued. Client stated I feel hopeless "
            "and worthless. I can't get out of bed most days. I have no energy "
            "and I've been crying all the time. Nothing makes me happy anymore. "
            "I'm struggling with my relationship. My partner doesn't understand. "
            "I feel sad all the time. I've been sleeping too much."
        ),
        modality="individual",
        presenting_concerns=["major depression", "relationship issues"],
    )


class TestSOAPNoteGenerator:
    def test_generate_produces_soap_note(self, anxiety_session: Session) -> None:
        gen = SOAPNoteGenerator()
        note = gen.generate(anxiety_session)

        assert note.session_id == "S001"
        assert note.client_id == "C001"
        assert len(note.subjective) > 0
        assert len(note.objective) > 0
        assert len(note.assessment) > 0
        assert len(note.plan) > 0

    def test_subjective_captures_feelings(self, anxiety_session: Session) -> None:
        gen = SOAPNoteGenerator()
        note = gen.generate(anxiety_session)
        # Should capture client's reported emotional experiences
        assert "emotional experiences" in note.subjective.lower() or "concerns" in note.subjective.lower()

    def test_objective_includes_affect(self, depression_session: Session) -> None:
        gen = SOAPNoteGenerator()
        note = gen.generate(depression_session)
        assert "affect" in note.objective.lower()

    def test_assessment_detects_anxiety(self, anxiety_session: Session) -> None:
        gen = SOAPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert "anxiety" in note.assessment.lower()

    def test_plan_includes_interventions(self, anxiety_session: Session) -> None:
        gen = SOAPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert "therapy" in note.plan.lower() or "session" in note.plan.lower()

    def test_depression_assessment(self, depression_session: Session) -> None:
        gen = SOAPNoteGenerator()
        note = gen.generate(depression_session)
        assert "depress" in note.assessment.lower()

    def test_tearful_observation(self, depression_session: Session) -> None:
        gen = SOAPNoteGenerator()
        note = gen.generate(depression_session)
        assert "tearful" in note.objective.lower()


class TestDAPNoteGenerator:
    def test_generate_produces_dap_note(self, anxiety_session: Session) -> None:
        gen = DAPNoteGenerator()
        note = gen.generate(anxiety_session)

        assert note.session_id == "S001"
        assert len(note.data) > 0
        assert len(note.assessment) > 0
        assert len(note.plan) > 0

    def test_data_includes_session_info(self, anxiety_session: Session) -> None:
        gen = DAPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert "Session #3" in note.data
        assert "50 minutes" in note.data

    def test_data_captures_emotions(self, depression_session: Session) -> None:
        gen = DAPNoteGenerator()
        note = gen.generate(depression_session)
        assert "emotions" in note.data.lower() or "tearful" in note.data.lower()

    def test_plan_is_numbered(self, anxiety_session: Session) -> None:
        gen = DAPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert "1." in note.plan


class TestBIRPNoteGenerator:
    def test_generate_produces_birp_note(self, anxiety_session: Session) -> None:
        gen = BIRPNoteGenerator()
        note = gen.generate(anxiety_session)

        assert note.session_id == "S001"
        assert len(note.behavior) > 0
        assert len(note.intervention) > 0
        assert len(note.response) > 0
        assert len(note.plan) > 0

    def test_behavior_includes_session_info(self, anxiety_session: Session) -> None:
        gen = BIRPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert "50-minute" in note.behavior

    def test_intervention_lists_techniques(self, anxiety_session: Session) -> None:
        gen = BIRPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert "intervention" in note.intervention.lower()

    def test_response_assesses_engagement(self, anxiety_session: Session) -> None:
        gen = BIRPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert len(note.response) > 20

    def test_plan_includes_continuation(self, anxiety_session: Session) -> None:
        gen = BIRPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert "continue" in note.plan.lower()

    def test_presenting_concerns_in_behavior(self, anxiety_session: Session) -> None:
        gen = BIRPNoteGenerator()
        note = gen.generate(anxiety_session)
        assert "generalized anxiety" in note.behavior.lower() or "panic" in note.behavior.lower()
