"""Tests for data models."""

import pytest
from pydantic import ValidationError

from sessionnotes.models import (
    BIRPNote,
    DAPNote,
    NoteFormat,
    ProgressEntry,
    RiskCategory,
    RiskFlag,
    RiskLevel,
    Session,
    SOAPNote,
    Theme,
)


class TestSession:
    def test_create_session(self) -> None:
        session = Session(
            session_id="S001",
            client_id="C001",
            transcript="Client discussed anxiety.",
        )
        assert session.session_id == "S001"
        assert session.duration_minutes == 50
        assert session.modality == "individual"
        assert session.session_number == 1

    def test_session_requires_transcript(self) -> None:
        with pytest.raises(ValidationError):
            Session(session_id="S001", client_id="C001")

    def test_session_invalid_duration(self) -> None:
        with pytest.raises(ValidationError):
            Session(
                session_id="S001", client_id="C001",
                transcript="test", duration_minutes=0,
            )


class TestSOAPNote:
    def test_create_soap_note(self) -> None:
        note = SOAPNote(
            session_id="S001",
            client_id="C001",
            subjective="Client reports anxiety.",
            objective="Client appeared tense.",
            assessment="GAD symptoms present.",
            plan="Continue CBT.",
        )
        assert note.session_id == "S001"
        assert note.subjective == "Client reports anxiety."


class TestDAPNote:
    def test_create_dap_note(self) -> None:
        note = DAPNote(
            session_id="S001",
            client_id="C001",
            data="Client discussed work stress.",
            assessment="Adjustment disorder.",
            plan="Coping skills training.",
        )
        assert note.data == "Client discussed work stress."


class TestBIRPNote:
    def test_create_birp_note(self) -> None:
        note = BIRPNote(
            session_id="S001",
            client_id="C001",
            behavior="Client arrived on time.",
            intervention="Used CBT techniques.",
            response="Client was receptive.",
            plan="Continue weekly sessions.",
        )
        assert note.behavior == "Client arrived on time."


class TestTheme:
    def test_create_theme(self) -> None:
        theme = Theme(
            name="Anxiety",
            category="emotional",
            frequency=5,
            keywords=["anxious", "worry"],
        )
        assert theme.name == "Anxiety"
        assert theme.severity == "moderate"


class TestRiskFlag:
    def test_create_risk_flag(self) -> None:
        flag = RiskFlag(
            category=RiskCategory.SUICIDAL_IDEATION,
            level=RiskLevel.HIGH,
            indicator="want to die",
            context="Client stated they want to die",
            recommended_action="Safety assessment needed",
        )
        assert flag.requires_immediate_action is False

    def test_risk_levels(self) -> None:
        assert RiskLevel.CRITICAL.value == "critical"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.NONE.value == "none"


class TestNoteFormat:
    def test_note_formats(self) -> None:
        assert NoteFormat.SOAP.value == "soap"
        assert NoteFormat.DAP.value == "dap"
        assert NoteFormat.BIRP.value == "birp"


class TestProgressEntry:
    def test_create_progress_entry(self) -> None:
        entry = ProgressEntry(
            session_id="S001",
            session_date="2025-01-15T10:00:00",
            session_number=1,
            mood_rating=6,
            functioning_level="moderate",
        )
        assert entry.mood_rating == 6

    def test_mood_rating_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ProgressEntry(
                session_id="S001",
                session_date="2025-01-15T10:00:00",
                session_number=1,
                mood_rating=11,
            )
