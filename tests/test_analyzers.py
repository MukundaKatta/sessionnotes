"""Tests for session analyzers."""

import pytest

from sessionnotes.analyzer.progress import ProgressTracker
from sessionnotes.analyzer.risk import RiskScreener
from sessionnotes.analyzer.themes import ThemeExtractor
from sessionnotes.models import RiskCategory, RiskLevel, Session


@pytest.fixture
def multi_theme_session() -> Session:
    return Session(
        session_id="S001",
        client_id="C001",
        transcript=(
            "Client discussed anxiety about work deadlines and feeling overwhelmed. "
            "Client expressed worry about relationship with partner, mentioning "
            "frequent arguments and communication breakdown. Client reported "
            "difficulty sleeping and racing thoughts. Client mentioned feeling "
            "lonely and isolated from friends. Client has been drinking more "
            "to cope with stress."
        ),
    )


@pytest.fixture
def high_risk_session() -> Session:
    return Session(
        session_id="S_RISK",
        client_id="C002",
        transcript=(
            "Client stated they have been thinking about suicide and feel "
            "like they want to die. Client reported cutting myself last week "
            "when overwhelmed. Client mentioned drinking more and binge drinking "
            "on weekends. Client feels hopeless and doesn't see the point "
            "of continuing."
        ),
    )


@pytest.fixture
def low_risk_session() -> Session:
    return Session(
        session_id="S_LOW",
        client_id="C003",
        transcript=(
            "Client reported feeling better this week. Made progress on goals. "
            "Client is coping well with work stress. Practiced breathing exercises "
            "daily. Client expressed motivation to continue therapy."
        ),
    )


class TestThemeExtractor:
    def test_extract_finds_themes(self, multi_theme_session: Session) -> None:
        extractor = ThemeExtractor()
        themes = extractor.extract(multi_theme_session)
        assert len(themes) > 0

    def test_extract_finds_anxiety(self, multi_theme_session: Session) -> None:
        extractor = ThemeExtractor()
        themes = extractor.extract(multi_theme_session)
        names = [t.name.lower() for t in themes]
        assert any("anxiety" in n for n in names)

    def test_extract_finds_relationship(self, multi_theme_session: Session) -> None:
        extractor = ThemeExtractor()
        themes = extractor.extract(multi_theme_session)
        names = [t.name.lower() for t in themes]
        assert any("relationship" in n for n in names)

    def test_extract_finds_substance(self, multi_theme_session: Session) -> None:
        extractor = ThemeExtractor()
        themes = extractor.extract(multi_theme_session)
        names = [t.name.lower() for t in themes]
        assert any("substance" in n for n in names)

    def test_themes_sorted_by_frequency(self, multi_theme_session: Session) -> None:
        extractor = ThemeExtractor()
        themes = extractor.extract(multi_theme_session)
        for i in range(len(themes) - 1):
            assert themes[i].frequency >= themes[i + 1].frequency

    def test_get_primary_themes_limits_count(self, multi_theme_session: Session) -> None:
        extractor = ThemeExtractor()
        primary = extractor.get_primary_themes(multi_theme_session, max_themes=2)
        assert len(primary) <= 2

    def test_themes_have_category(self, multi_theme_session: Session) -> None:
        extractor = ThemeExtractor()
        themes = extractor.extract(multi_theme_session)
        for theme in themes:
            assert theme.category in [
                "emotional", "relational", "clinical", "cognitive",
                "situational", "behavioral", "somatic", "developmental",
            ]

    def test_compare_themes_across_sessions(self) -> None:
        extractor = ThemeExtractor()
        sessions = [
            Session(
                session_id="S1", client_id="C1", session_number=1,
                transcript="Client feels anxious and worried about work.",
            ),
            Session(
                session_id="S2", client_id="C1", session_number=2,
                transcript="Client still anxious. Also discussed relationship conflict with partner.",
            ),
        ]
        comparison = extractor.compare_themes(sessions)
        assert "Anxiety" in comparison
        assert len(comparison["Anxiety"]) == 2


class TestRiskScreener:
    def test_screen_high_risk(self, high_risk_session: Session) -> None:
        screener = RiskScreener()
        flags = screener.screen(high_risk_session)
        assert len(flags) > 0
        levels = [f.level for f in flags]
        assert RiskLevel.HIGH in levels or RiskLevel.CRITICAL in levels

    def test_screen_low_risk(self, low_risk_session: Session) -> None:
        screener = RiskScreener()
        flags = screener.screen(low_risk_session)
        # Should have no or only low-level flags
        high_flags = [f for f in flags if f.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)]
        assert len(high_flags) == 0

    def test_detects_suicidal_ideation(self, high_risk_session: Session) -> None:
        screener = RiskScreener()
        flags = screener.screen(high_risk_session)
        categories = [f.category for f in flags]
        assert RiskCategory.SUICIDAL_IDEATION in categories

    def test_detects_self_harm(self, high_risk_session: Session) -> None:
        screener = RiskScreener()
        flags = screener.screen(high_risk_session)
        categories = [f.category for f in flags]
        assert RiskCategory.SELF_HARM in categories

    def test_detects_substance_abuse(self, high_risk_session: Session) -> None:
        screener = RiskScreener()
        flags = screener.screen(high_risk_session)
        categories = [f.category for f in flags]
        assert RiskCategory.SUBSTANCE_ABUSE in categories

    def test_overall_risk_level(self, high_risk_session: Session) -> None:
        screener = RiskScreener()
        level = screener.get_overall_risk_level(high_risk_session)
        assert level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    def test_requires_immediate_action(self, high_risk_session: Session) -> None:
        screener = RiskScreener()
        assert screener.requires_immediate_action(high_risk_session)

    def test_no_immediate_action_low_risk(self, low_risk_session: Session) -> None:
        screener = RiskScreener()
        assert not screener.requires_immediate_action(low_risk_session)

    def test_flags_have_context(self, high_risk_session: Session) -> None:
        screener = RiskScreener()
        flags = screener.screen(high_risk_session)
        for flag in flags:
            assert len(flag.context) > 0
            assert len(flag.recommended_action) > 0

    def test_deduplication(self, high_risk_session: Session) -> None:
        screener = RiskScreener()
        flags = screener.screen(high_risk_session)
        categories = [f.category for f in flags]
        # Each category should appear at most once
        assert len(categories) == len(set(categories))


class TestProgressTracker:
    def test_create_entry(self) -> None:
        tracker = ProgressTracker()
        session = Session(
            session_id="S1", client_id="C1", session_number=1,
            transcript="Client reported feeling anxious and stressed about work.",
        )
        entry = tracker.create_entry(session)
        assert entry.session_id == "S1"
        assert entry.mood_rating is not None
        assert 1 <= entry.mood_rating <= 10

    def test_track_progress_multiple_sessions(self) -> None:
        tracker = ProgressTracker()
        sessions = [
            Session(
                session_id=f"S{i}", client_id="C1", session_number=i,
                transcript=t,
            )
            for i, t in enumerate(
                [
                    "Client very depressed, hopeless, can't function.",
                    "Client slightly better, still struggling but coping.",
                    "Client improved, managing well, feeling hopeful and motivated.",
                ],
                start=1,
            )
        ]
        entries = tracker.track_progress(sessions)
        assert len(entries) == 3
        assert entries[0].session_number == 1
        assert entries[2].session_number == 3

    def test_trajectory_improving(self) -> None:
        tracker = ProgressTracker()
        sessions = [
            Session(
                session_id=f"S{i}", client_id="C1", session_number=i,
                transcript=t,
            )
            for i, t in enumerate(
                [
                    "Client depressed hopeless worthless deteriorating.",
                    "Client still sad but slightly better managing.",
                    "Client improved progress coping hopeful motivated confident.",
                ],
                start=1,
            )
        ]
        trajectory = tracker.get_trajectory(sessions)
        assert trajectory["mood_trend"] in ("improving", "stable")
        assert trajectory["total_sessions"] == 3

    def test_functioning_assessment(self) -> None:
        tracker = ProgressTracker()
        session = Session(
            session_id="S1", client_id="C1",
            transcript="Client can't function, unable to work, isolated at home.",
        )
        entry = tracker.create_entry(session)
        assert entry.functioning_level == "low"
