"""BIRP Note Generator - Behavior, Intervention, Response, Plan."""

from __future__ import annotations

import re

from sessionnotes.models import Session, BIRPNote


class BIRPNoteGenerator:
    """Generate BIRP format therapy notes from session transcripts.

    BIRP notes focus on observable behaviors and therapeutic interventions:
    - Behavior: What the client did/said (observable)
    - Intervention: What the therapist did
    - Response: How the client responded to interventions
    - Plan: Next steps
    """

    BEHAVIOR_INDICATORS = {
        "verbal": [
            "discussed", "reported", "stated", "described", "expressed",
            "disclosed", "mentioned", "shared", "denied", "endorsed",
        ],
        "nonverbal": [
            "tearful", "crying", "fidgeting", "restless", "agitated",
            "calm", "smiling", "avoiding eye contact", "crossed arms",
            "leaning forward", "nodding", "shaking head",
        ],
        "mood": [
            "anxious", "depressed", "angry", "frustrated", "hopeful",
            "sad", "happy", "irritable", "flat", "labile",
        ],
        "engagement": [
            "cooperative", "resistant", "withdrawn", "engaged", "motivated",
            "distracted", "attentive", "defensive", "open",
        ],
    }

    INTERVENTION_TECHNIQUES = {
        "active_listening": {
            "keywords": ["listened", "reflected", "paraphrased", "summarized"],
            "description": "Active listening and reflective techniques",
        },
        "cognitive_restructuring": {
            "keywords": ["thought", "belief", "cognitive", "reframe", "distortion",
                         "automatic thought", "thinking pattern"],
            "description": "Cognitive restructuring to identify and challenge maladaptive thought patterns",
        },
        "psychoeducation": {
            "keywords": ["explained", "educated", "taught", "information",
                         "psychoeducation", "normalize"],
            "description": "Psychoeducation regarding symptoms and coping strategies",
        },
        "mindfulness": {
            "keywords": ["mindfulness", "meditation", "breathing", "grounding",
                         "present moment", "awareness"],
            "description": "Mindfulness-based techniques including guided meditation and grounding exercises",
        },
        "behavioral": {
            "keywords": ["behavior", "activity", "schedule", "exposure",
                         "homework", "practice", "skill"],
            "description": "Behavioral interventions including activity scheduling and skills practice",
        },
        "supportive": {
            "keywords": ["support", "validate", "empathy", "normalize",
                         "encourage"],
            "description": "Supportive therapy techniques including validation and encouragement",
        },
        "solution_focused": {
            "keywords": ["solution", "goal", "exception", "scaling", "miracle"],
            "description": "Solution-focused interventions exploring exceptions and strengths",
        },
        "trauma_focused": {
            "keywords": ["trauma", "processing", "narrative", "emdr", "exposure",
                         "desensitization"],
            "description": "Trauma-focused interventions with appropriate pacing and stabilization",
        },
    }

    RESPONSE_POSITIVE = [
        "understood", "agreed", "practiced", "engaged", "willing",
        "receptive", "insightful", "motivated", "hopeful", "committed",
        "acknowledged", "reflected", "realized", "insight",
    ]

    RESPONSE_NEGATIVE = [
        "resistant", "refused", "skeptical", "dismissive", "avoidant",
        "defensive", "shut down", "withdrawn", "disagreed", "unwilling",
    ]

    def generate(self, session: Session) -> BIRPNote:
        """Generate a BIRP note from a therapy session."""
        transcript_lower = session.transcript.lower()

        behavior = self._extract_behavior(session, transcript_lower)
        intervention = self._extract_intervention(transcript_lower)
        response = self._assess_response(transcript_lower)
        plan = self._generate_plan(session, transcript_lower)

        return BIRPNote(
            session_id=session.session_id,
            client_id=session.client_id,
            session_date=session.session_date,
            behavior=behavior,
            intervention=intervention,
            response=response,
            plan=plan,
        )

    def _extract_behavior(self, session: Session, transcript_lower: str) -> str:
        """Extract observable behaviors from the transcript."""
        parts: list[str] = []

        # Presenting behavior
        parts.append(
            f"Client attended scheduled {session.duration_minutes}-minute "
            f"{session.modality} therapy session."
        )

        # Mood and affect
        moods = [m for m in self.BEHAVIOR_INDICATORS["mood"] if m in transcript_lower]
        if moods:
            parts.append(f"Client's mood was described as {', '.join(moods[:3])}.")

        # Engagement
        engagement = [e for e in self.BEHAVIOR_INDICATORS["engagement"] if e in transcript_lower]
        if engagement:
            parts.append(f"Client was {', '.join(engagement[:2])} during the session.")
        else:
            parts.append("Client was cooperative during the session.")

        # Nonverbal behaviors
        nonverbal = [n for n in self.BEHAVIOR_INDICATORS["nonverbal"] if n in transcript_lower]
        if nonverbal:
            parts.append(f"Nonverbal behavior included: {', '.join(nonverbal[:3])}.")

        # Key behavioral content
        sentences = re.split(r'[.!?]+', session.transcript)
        behavioral_content: list[str] = []
        for sentence in sentences:
            s_lower = sentence.lower().strip()
            if any(v in s_lower for v in self.BEHAVIOR_INDICATORS["verbal"]):
                cleaned = sentence.strip()
                if len(cleaned) > 20:
                    behavioral_content.append(cleaned)

        if behavioral_content:
            parts.append(
                "Client discussed the following: "
                + "; ".join(behavioral_content[:3])
                + "."
            )

        # Presenting concerns
        if session.presenting_concerns:
            parts.append(
                "Presenting concerns addressed: "
                + ", ".join(session.presenting_concerns)
                + "."
            )

        return " ".join(parts)

    def _extract_intervention(self, transcript_lower: str) -> str:
        """Identify and describe therapeutic interventions used."""
        interventions: list[str] = []

        for technique_info in self.INTERVENTION_TECHNIQUES.values():
            if any(kw in transcript_lower for kw in technique_info["keywords"]):
                interventions.append(technique_info["description"])

        if not interventions:
            interventions.append(
                "Active listening and reflective techniques"
            )
            interventions.append(
                "Supportive therapy techniques including validation and encouragement"
            )

        # Format as numbered list
        formatted = []
        for i, intervention in enumerate(interventions[:5], 1):
            formatted.append(f"{i}. {intervention}")

        return "Therapist utilized the following interventions: " + ". ".join(formatted) + "."

    def _assess_response(self, transcript_lower: str) -> str:
        """Assess client's response to interventions."""
        parts: list[str] = []

        positive = [r for r in self.RESPONSE_POSITIVE if r in transcript_lower]
        negative = [r for r in self.RESPONSE_NEGATIVE if r in transcript_lower]

        if len(positive) > len(negative):
            parts.append(
                "Client responded positively to therapeutic interventions."
            )
            if "insight" in positive or "realized" in positive:
                parts.append("Client demonstrated emerging insight into presenting concerns.")
            if "practiced" in positive or "engaged" in positive:
                parts.append("Client actively engaged in therapeutic exercises during session.")
            if "motivated" in positive or "committed" in positive:
                parts.append("Client expressed motivation to continue working on treatment goals.")
        elif len(negative) > len(positive):
            parts.append(
                "Client showed some resistance to therapeutic interventions."
            )
            if "avoidant" in negative or "defensive" in negative:
                parts.append(
                    "Client exhibited avoidance when certain topics were explored; "
                    "therapeutic alliance maintained."
                )
            if "withdrawn" in negative:
                parts.append("Client became withdrawn; session adapted to meet client's needs.")
        else:
            parts.append(
                "Client was receptive to therapeutic interventions and "
                "engaged appropriately in session."
            )

        # Check for specific responses
        if any(w in transcript_lower for w in ["homework", "assignment", "between session"]):
            if any(w in transcript_lower for w in ["completed", "did", "tried", "practiced"]):
                parts.append("Client completed between-session assignments.")
            elif any(w in transcript_lower for w in ["forgot", "didn't", "unable"]):
                parts.append(
                    "Client did not complete between-session assignments; "
                    "barriers were explored."
                )

        if not parts:
            parts.append(
                "Client participated in session and was responsive to "
                "therapeutic interventions."
            )

        return " ".join(parts)

    def _generate_plan(self, session: Session, transcript_lower: str) -> str:
        """Generate treatment plan section."""
        plans: list[str] = []

        plans.append(
            f"1. Continue {session.modality} therapy sessions at current frequency."
        )

        plan_num = 2

        # Content-specific plans
        if any(w in transcript_lower for w in ["anxiety", "anxious", "panic", "worry"]):
            plans.append(
                f"{plan_num}. Continue anxiety management skills training; "
                f"assign daily practice of coping techniques."
            )
            plan_num += 1

        if any(w in transcript_lower for w in ["depression", "depressed", "sad", "hopeless"]):
            plans.append(
                f"{plan_num}. Continue behavioral activation; "
                f"assign mood monitoring between sessions."
            )
            plan_num += 1

        if any(w in transcript_lower for w in ["trauma", "ptsd", "abuse"]):
            plans.append(
                f"{plan_num}. Continue trauma processing at appropriate pace; "
                f"reinforce stabilization techniques."
            )
            plan_num += 1

        if any(w in transcript_lower for w in ["relationship", "partner", "marriage"]):
            plans.append(
                f"{plan_num}. Continue exploring relational patterns; "
                f"consider couples/family session if appropriate."
            )
            plan_num += 1

        if any(w in transcript_lower for w in ["substance", "alcohol", "drug", "drinking"]):
            plans.append(
                f"{plan_num}. Monitor substance use; coordinate with substance abuse "
                f"treatment if indicated."
            )
            plan_num += 1

        # Safety planning
        if any(w in transcript_lower for w in ["suicidal", "self-harm", "kill"]):
            plans.append(
                f"{plan_num}. SAFETY: Update safety plan. Ensure client has crisis "
                f"resources (988 Suicide & Crisis Lifeline). Assess need for "
                f"higher level of care."
            )
            plan_num += 1

        plans.append(
            f"{plan_num}. Review treatment goals and progress in next session."
        )

        return " ".join(plans)
