"""Risk screening for therapy session transcripts."""

from __future__ import annotations

from sessionnotes.models import RiskCategory, RiskFlag, RiskLevel, Session


class RiskScreener:
    """Screen therapy transcripts for safety concerns and risk factors.

    Flags potential risks including suicidal ideation, self-harm,
    homicidal ideation, substance abuse, and other safety concerns.
    """

    RISK_PATTERNS: dict[RiskCategory, dict] = {
        RiskCategory.SUICIDAL_IDEATION: {
            "critical": [
                "plan to kill myself", "going to end it", "going to end my life",
                "method to die", "written a note", "suicide note",
                "said goodbye to everyone", "giving away possessions",
                "have a plan to die", "date to end it",
            ],
            "high": [
                "want to die", "wish i was dead", "better off dead",
                "kill myself", "end my life", "suicidal",
                "no reason to live", "can't go on", "life isn't worth",
                "thinking about suicide", "don't want to be alive",
            ],
            "moderate": [
                "hopeless", "don't see the point", "what's the point",
                "no future", "nothing to live for", "not worth it",
                "everyone would be better off without me",
                "don't want to wake up",
            ],
            "low": [
                "feeling down", "life is hard", "struggling",
                "don't know how much more i can take",
                "at my limit", "breaking point",
            ],
        },
        RiskCategory.SELF_HARM: {
            "critical": [
                "cutting myself", "burning myself", "hurt myself badly",
                "overdosed", "took too many pills",
            ],
            "high": [
                "self-harm", "hurting myself", "cut myself",
                "want to hurt myself", "punish myself physically",
                "hitting myself", "scratching myself",
            ],
            "moderate": [
                "urge to hurt myself", "thinking about cutting",
                "used to self-harm", "relapsed on self-harm",
                "scars from cutting",
            ],
            "low": [
                "sometimes i want to feel pain",
                "physical pain is easier than emotional",
            ],
        },
        RiskCategory.HOMICIDAL_IDEATION: {
            "critical": [
                "plan to kill", "going to hurt someone", "going to kill",
                "weapon", "going to attack",
            ],
            "high": [
                "want to kill", "hurt someone", "violent thoughts",
                "homicidal", "fantasize about hurting",
            ],
            "moderate": [
                "so angry i could", "rage", "violent urges",
                "want to punch", "destroy",
            ],
            "low": [
                "angry at", "resentful toward", "hate them",
            ],
        },
        RiskCategory.SUBSTANCE_ABUSE: {
            "critical": [
                "overdosed", "blackout", "detox", "withdrawal symptoms",
                "can't stop using", "using every day",
            ],
            "high": [
                "relapsed", "binge drinking", "using drugs again",
                "can't control my drinking", "need it to function",
                "drinking alone", "hiding my use",
            ],
            "moderate": [
                "drinking more", "using more", "craving",
                "hard to stay sober", "tempted to use",
                "social drinking getting worse",
            ],
            "low": [
                "drink to cope", "occasional use", "wine to relax",
                "smoke when stressed",
            ],
        },
        RiskCategory.PSYCHOSIS: {
            "high": [
                "hearing voices", "seeing things that aren't there",
                "paranoid", "people are watching me", "being followed",
                "government is tracking", "messages from tv",
                "mind control",
            ],
            "moderate": [
                "losing touch with reality", "can't tell what's real",
                "suspicious of everyone", "conspiracy",
            ],
            "low": [
                "feeling disconnected from reality", "dissociating",
                "feel like i'm in a dream",
            ],
        },
        RiskCategory.ABUSE_NEGLECT: {
            "critical": [
                "being beaten", "being abused", "hit me", "sexual abuse",
                "child abuse", "elder abuse", "locked in",
            ],
            "high": [
                "partner hits me", "afraid of my partner", "controlling",
                "won't let me leave", "threatens me", "forced me",
                "domestic violence",
            ],
            "moderate": [
                "emotionally abusive", "manipulative", "gaslighting",
                "verbally abusive", "intimidation",
            ],
            "low": [
                "unhealthy relationship", "power imbalance", "feels unsafe",
            ],
        },
        RiskCategory.EATING_DISORDER: {
            "high": [
                "purging", "binging and purging", "starving myself",
                "haven't eaten in days", "making myself throw up",
                "laxatives to lose weight",
            ],
            "moderate": [
                "restricting food", "binge eating", "obsessed with weight",
                "body dysmorphia", "afraid of food", "counting every calorie",
            ],
            "low": [
                "skipping meals", "not hungry", "eating too much",
                "emotional eating", "stress eating",
            ],
        },
        RiskCategory.SEVERE_DEPRESSION: {
            "high": [
                "can't get out of bed", "not bathing", "stopped caring",
                "completely numb", "can't function", "lost all motivation",
                "haven't left the house in weeks",
            ],
            "moderate": [
                "no energy", "no motivation", "can't concentrate",
                "lost interest in everything", "sleeping all day",
                "crying all the time",
            ],
            "low": [
                "feeling low", "less interested", "tired a lot",
                "hard to focus", "appetite changes",
            ],
        },
    }

    RECOMMENDED_ACTIONS = {
        RiskLevel.CRITICAL: (
            "IMMEDIATE ACTION REQUIRED: Conduct thorough safety assessment. "
            "Consider emergency services (911), psychiatric emergency evaluation, "
            "or voluntary/involuntary hospitalization. Contact supervisor immediately. "
            "Document all actions taken."
        ),
        RiskLevel.HIGH: (
            "Complete comprehensive safety assessment. Develop or update safety plan. "
            "Increase session frequency. Consider referral for psychiatric evaluation. "
            "Consult with supervisor. Ensure client has crisis resources "
            "(988 Suicide & Crisis Lifeline)."
        ),
        RiskLevel.MODERATE: (
            "Monitor closely. Review and reinforce coping strategies. "
            "Assess for changes in risk level. Consider increasing session frequency. "
            "Provide psychoeducation and crisis resources."
        ),
        RiskLevel.LOW: (
            "Continue monitoring. Address in therapeutic context. "
            "Strengthen protective factors and coping skills."
        ),
    }

    def screen(self, session: Session) -> list[RiskFlag]:
        """Screen a therapy session transcript for risk factors."""
        transcript_lower = session.transcript.lower()
        flags: list[RiskFlag] = []

        for category, severity_patterns in self.RISK_PATTERNS.items():
            for severity_str, patterns in severity_patterns.items():
                level = RiskLevel(severity_str)
                for pattern in patterns:
                    if pattern in transcript_lower:
                        idx = transcript_lower.index(pattern)
                        start = max(0, idx - 50)
                        end = min(len(transcript_lower), idx + len(pattern) + 50)
                        context = session.transcript[start:end].strip()

                        flags.append(
                            RiskFlag(
                                category=category,
                                level=level,
                                indicator=pattern,
                                context=f"...{context}...",
                                recommended_action=self.RECOMMENDED_ACTIONS.get(
                                    level, ""
                                ),
                                requires_immediate_action=level
                                in (RiskLevel.CRITICAL, RiskLevel.HIGH),
                            )
                        )

        # Deduplicate by category, keeping highest severity
        flags = self._deduplicate_flags(flags)
        # Sort by severity
        severity_order = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MODERATE: 2,
            RiskLevel.LOW: 3,
        }
        flags.sort(key=lambda f: severity_order.get(f.level, 99))

        return flags

    def _deduplicate_flags(self, flags: list[RiskFlag]) -> list[RiskFlag]:
        """Keep only the highest-severity flag per category."""
        severity_rank = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MODERATE: 2,
            RiskLevel.LOW: 3,
        }
        best: dict[RiskCategory, RiskFlag] = {}
        for flag in flags:
            existing = best.get(flag.category)
            if existing is None or severity_rank[flag.level] < severity_rank[existing.level]:
                best[flag.category] = flag
        return list(best.values())

    def get_overall_risk_level(self, session: Session) -> RiskLevel:
        """Get the highest risk level found in a session."""
        flags = self.screen(session)
        if not flags:
            return RiskLevel.NONE

        severity_rank = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MODERATE: 2,
            RiskLevel.LOW: 3,
            RiskLevel.NONE: 4,
        }
        return min(flags, key=lambda f: severity_rank[f.level]).level

    def requires_immediate_action(self, session: Session) -> bool:
        """Check if any flags require immediate clinical action."""
        flags = self.screen(session)
        return any(f.requires_immediate_action for f in flags)
