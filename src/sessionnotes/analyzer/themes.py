"""Theme extraction from therapy session transcripts."""

from __future__ import annotations

from sessionnotes.models import Session, Theme


class ThemeExtractor:
    """Identify themes and topics from therapy session transcripts."""

    THEME_DEFINITIONS: dict[str, dict] = {
        "anxiety": {
            "category": "emotional",
            "keywords": [
                "anxious", "anxiety", "worry", "worried", "panic", "nervous",
                "fear", "afraid", "dread", "apprehensive", "tense", "on edge",
                "racing thoughts", "catastrophizing", "what if",
            ],
            "description_template": "Client expressed anxiety-related concerns",
        },
        "depression": {
            "category": "emotional",
            "keywords": [
                "depressed", "depression", "sad", "hopeless", "worthless",
                "empty", "numb", "tired", "fatigue", "no energy",
                "can't get out of bed", "don't care", "nothing matters",
                "crying", "tearful", "no motivation",
            ],
            "description_template": "Client exhibited depressive symptomatology",
        },
        "anger": {
            "category": "emotional",
            "keywords": [
                "angry", "anger", "furious", "rage", "irritable", "annoyed",
                "frustrated", "hostile", "resentment", "bitter", "mad",
            ],
            "description_template": "Client discussed anger-related experiences",
        },
        "grief_and_loss": {
            "category": "emotional",
            "keywords": [
                "grief", "loss", "death", "died", "mourning", "bereavement",
                "missing", "funeral", "gone", "passed away", "lost someone",
            ],
            "description_template": "Client processing grief and loss",
        },
        "relationship_conflict": {
            "category": "relational",
            "keywords": [
                "conflict", "argument", "fight", "disagreement", "tension",
                "partner", "spouse", "marriage", "divorce", "separation",
                "cheating", "infidelity", "trust issues", "communication",
                "breakup", "dating",
            ],
            "description_template": "Client discussed relational conflicts",
        },
        "family_dynamics": {
            "category": "relational",
            "keywords": [
                "family", "mother", "father", "parent", "sibling", "brother",
                "sister", "child", "children", "in-laws", "household",
                "upbringing", "childhood", "generational",
            ],
            "description_template": "Client explored family dynamics and relationships",
        },
        "attachment": {
            "category": "relational",
            "keywords": [
                "attachment", "abandonment", "clingy", "needy", "avoidant",
                "dependent", "codependent", "enmeshed", "boundaries",
                "rejection", "fear of abandonment",
            ],
            "description_template": "Attachment-related themes emerged in session",
        },
        "trauma": {
            "category": "clinical",
            "keywords": [
                "trauma", "ptsd", "abuse", "assault", "violence", "neglect",
                "flashback", "nightmare", "hypervigilance", "triggered",
                "traumatic", "survivor", "victimization",
            ],
            "description_template": "Trauma-related content was discussed",
        },
        "self_esteem": {
            "category": "cognitive",
            "keywords": [
                "self-esteem", "confidence", "worthless", "inadequate",
                "not good enough", "failure", "self-worth", "self-image",
                "imposter", "comparison", "insecure", "shame",
            ],
            "description_template": "Self-esteem and self-worth themes were present",
        },
        "work_stress": {
            "category": "situational",
            "keywords": [
                "work", "job", "career", "boss", "coworker", "workplace",
                "burnout", "overworked", "deadline", "performance",
                "fired", "laid off", "promotion", "work-life balance",
            ],
            "description_template": "Work-related stressors were discussed",
        },
        "substance_use": {
            "category": "behavioral",
            "keywords": [
                "alcohol", "drinking", "drugs", "substance", "addiction",
                "sober", "relapse", "recovery", "using", "high", "drunk",
                "withdrawal", "craving", "habit",
            ],
            "description_template": "Substance use concerns were addressed",
        },
        "sleep_issues": {
            "category": "somatic",
            "keywords": [
                "sleep", "insomnia", "can't sleep", "nightmares", "oversleeping",
                "restless", "sleep schedule", "exhausted", "tired all the time",
            ],
            "description_template": "Sleep disturbances were reported",
        },
        "coping_skills": {
            "category": "behavioral",
            "keywords": [
                "coping", "strategy", "technique", "mindfulness", "breathing",
                "journaling", "exercise", "self-care", "relaxation",
                "grounding", "meditation", "healthy habits",
            ],
            "description_template": "Coping skills and strategies were explored",
        },
        "identity": {
            "category": "developmental",
            "keywords": [
                "identity", "who am i", "purpose", "meaning", "values",
                "sexuality", "gender", "cultural", "spiritual", "religious",
                "existential", "belonging",
            ],
            "description_template": "Identity-related exploration occurred",
        },
        "social_isolation": {
            "category": "relational",
            "keywords": [
                "lonely", "alone", "isolated", "no friends", "withdrawn",
                "social anxiety", "avoidance", "disconnected", "excluded",
            ],
            "description_template": "Social isolation and loneliness themes emerged",
        },
    }

    def extract(self, session: Session) -> list[Theme]:
        """Extract themes from a therapy session transcript."""
        transcript_lower = session.transcript.lower()
        themes: list[Theme] = []

        for theme_name, definition in self.THEME_DEFINITIONS.items():
            matched_keywords: list[str] = []
            frequency = 0

            for keyword in definition["keywords"]:
                count = transcript_lower.count(keyword)
                if count > 0:
                    matched_keywords.append(keyword)
                    frequency += count

            if matched_keywords:
                severity = self._assess_severity(frequency, len(matched_keywords))
                themes.append(
                    Theme(
                        name=theme_name.replace("_", " ").title(),
                        category=definition["category"],
                        frequency=frequency,
                        keywords=matched_keywords,
                        description=definition["description_template"],
                        severity=severity,
                    )
                )

        # Sort by frequency descending
        themes.sort(key=lambda t: t.frequency, reverse=True)
        return themes

    def _assess_severity(self, frequency: int, keyword_count: int) -> str:
        """Assess theme severity based on frequency and breadth."""
        score = frequency + keyword_count * 2
        if score >= 15:
            return "high"
        elif score >= 8:
            return "moderate"
        elif score >= 4:
            return "mild"
        return "minimal"

    def get_primary_themes(self, session: Session, max_themes: int = 3) -> list[Theme]:
        """Get the top themes from a session."""
        all_themes = self.extract(session)
        return all_themes[:max_themes]

    def compare_themes(
        self, sessions: list[Session]
    ) -> dict[str, list[dict[str, int | str]]]:
        """Compare themes across multiple sessions."""
        theme_history: dict[str, list[dict[str, int | str]]] = {}

        for session in sessions:
            themes = self.extract(session)
            for theme in themes:
                if theme.name not in theme_history:
                    theme_history[theme.name] = []
                theme_history[theme.name].append({
                    "session_id": session.session_id,
                    "session_number": session.session_number,
                    "frequency": theme.frequency,
                    "severity": theme.severity,
                })

        return theme_history
