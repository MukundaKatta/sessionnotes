"""Progress tracking across therapy sessions."""

from __future__ import annotations

from sessionnotes.analyzer.risk import RiskScreener
from sessionnotes.analyzer.themes import ThemeExtractor
from sessionnotes.models import ProgressEntry, Session


class ProgressTracker:
    """Track client progress across multiple therapy sessions."""

    POSITIVE_INDICATORS = [
        "better", "improved", "progress", "coping", "managing",
        "hopeful", "motivated", "insight", "breakthrough", "growth",
        "learned", "practicing", "applying", "accomplished", "achieved",
        "stable", "consistent", "resilient", "stronger", "confident",
    ]

    NEGATIVE_INDICATORS = [
        "worse", "deteriorating", "declining", "regressed", "relapsed",
        "crisis", "hospitalization", "suicidal", "self-harm",
        "not improving", "stuck", "stagnant", "resistant", "avoidant",
        "escalating", "worsening", "decompensating",
    ]

    FUNCTIONING_KEYWORDS = {
        "high": ["functioning well", "independent", "managing", "productive",
                 "social", "active", "engaged", "working"],
        "moderate": ["some difficulty", "struggling at times", "variable",
                     "inconsistent", "coping with support"],
        "low": ["unable to", "can't function", "not working", "isolated",
                "bedridden", "crisis", "hospitalized", "non-functional"],
    }

    def __init__(self) -> None:
        self.theme_extractor = ThemeExtractor()
        self.risk_screener = RiskScreener()

    def create_entry(self, session: Session) -> ProgressEntry:
        """Create a progress entry for a single session."""
        transcript_lower = session.transcript.lower()

        themes = self.theme_extractor.extract(session)
        risk_flags = self.risk_screener.screen(session)
        mood_rating = self._estimate_mood_rating(transcript_lower)
        functioning = self._assess_functioning(transcript_lower)
        goals_progress = self._assess_goals(transcript_lower)

        return ProgressEntry(
            session_id=session.session_id,
            session_date=session.session_date,
            session_number=session.session_number,
            themes=themes,
            risk_flags=risk_flags,
            mood_rating=mood_rating,
            functioning_level=functioning,
            goals_progress=goals_progress,
        )

    def track_progress(self, sessions: list[Session]) -> list[ProgressEntry]:
        """Track progress across multiple sessions."""
        entries = [self.create_entry(s) for s in sessions]
        entries.sort(key=lambda e: e.session_number)
        return entries

    def get_trajectory(self, sessions: list[Session]) -> dict:
        """Analyze overall treatment trajectory."""
        entries = self.track_progress(sessions)

        if not entries:
            return {"status": "no_data", "trend": "unknown"}

        mood_ratings = [e.mood_rating for e in entries if e.mood_rating is not None]
        risk_counts = [len(e.risk_flags) for e in entries]

        trajectory = {
            "total_sessions": len(entries),
            "mood_trend": self._calculate_trend(mood_ratings),
            "risk_trend": self._calculate_risk_trend(risk_counts),
            "recurring_themes": self._find_recurring_themes(entries),
            "overall_progress": self._assess_overall_progress(entries),
        }

        return trajectory

    def _estimate_mood_rating(self, transcript_lower: str) -> int:
        """Estimate a mood rating (1-10) from transcript content."""
        positive_count = sum(
            1 for w in self.POSITIVE_INDICATORS if w in transcript_lower
        )
        negative_count = sum(
            1 for w in self.NEGATIVE_INDICATORS if w in transcript_lower
        )

        base = 5
        score = base + positive_count - negative_count
        return max(1, min(10, score))

    def _assess_functioning(self, transcript_lower: str) -> str:
        """Assess client's functional level."""
        for level in ["low", "moderate", "high"]:
            keywords = self.FUNCTIONING_KEYWORDS[level]
            if any(kw in transcript_lower for kw in keywords):
                return level
        return "moderate"

    def _assess_goals(self, transcript_lower: str) -> dict[str, str]:
        """Assess progress toward common treatment goals."""
        goals: dict[str, str] = {}

        goal_areas = {
            "symptom_reduction": {
                "positive": ["symptoms improving", "less frequent", "reduced", "manageable"],
                "negative": ["symptoms worsening", "more frequent", "increased", "unmanageable"],
            },
            "coping_skills": {
                "positive": ["using coping", "practiced", "applied skills", "coping well"],
                "negative": ["not coping", "no strategies", "unable to cope"],
            },
            "relationship_improvement": {
                "positive": ["communicating better", "improved relationship", "closer"],
                "negative": ["more conflict", "relationship worse", "further apart"],
            },
        }

        for goal_name, indicators in goal_areas.items():
            pos = any(kw in transcript_lower for kw in indicators["positive"])
            neg = any(kw in transcript_lower for kw in indicators["negative"])
            if pos and not neg:
                goals[goal_name] = "improving"
            elif neg and not pos:
                goals[goal_name] = "declining"
            elif pos and neg:
                goals[goal_name] = "mixed"
            else:
                goals[goal_name] = "stable"

        return goals

    def _calculate_trend(self, values: list[int]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return "insufficient_data"

        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2:]

        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)

        diff = avg_second - avg_first
        if diff > 1:
            return "improving"
        elif diff < -1:
            return "declining"
        return "stable"

    def _calculate_risk_trend(self, risk_counts: list[int]) -> str:
        """Calculate risk trend."""
        if len(risk_counts) < 2:
            return "insufficient_data"

        if risk_counts[-1] > risk_counts[0]:
            return "increasing_risk"
        elif risk_counts[-1] < risk_counts[0]:
            return "decreasing_risk"
        return "stable_risk"

    def _find_recurring_themes(self, entries: list[ProgressEntry]) -> list[str]:
        """Find themes that appear across multiple sessions."""
        theme_counts: dict[str, int] = {}
        for entry in entries:
            for theme in entry.themes:
                theme_counts[theme.name] = theme_counts.get(theme.name, 0) + 1

        recurring = [
            name for name, count in theme_counts.items() if count >= 2
        ]
        return sorted(recurring, key=lambda n: theme_counts[n], reverse=True)

    def _assess_overall_progress(self, entries: list[ProgressEntry]) -> str:
        """Assess overall treatment progress."""
        if len(entries) < 2:
            return "too_early_to_assess"

        mood_ratings = [e.mood_rating for e in entries if e.mood_rating is not None]
        if not mood_ratings:
            return "insufficient_data"

        trend = self._calculate_trend(mood_ratings)
        latest_risk = len(entries[-1].risk_flags) if entries else 0

        if trend == "improving" and latest_risk == 0:
            return "positive_progress"
        elif trend == "declining" or latest_risk > 2:
            return "concerning_regression"
        elif trend == "stable":
            return "maintaining_gains"
        return "mixed_progress"
