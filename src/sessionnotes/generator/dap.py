"""DAP Note Generator - Data, Assessment, Plan."""

from __future__ import annotations

import re

from sessionnotes.models import Session, DAPNote


class DAPNoteGenerator:
    """Generate DAP format therapy notes from session transcripts.

    DAP notes consolidate subjective and objective into a single Data section:
    - Data: All information gathered (client reports + therapist observations)
    - Assessment: Clinical interpretation
    - Plan: Treatment direction
    """

    EMOTION_WORDS = [
        "angry", "anxious", "depressed", "sad", "happy", "hopeful",
        "frustrated", "overwhelmed", "lonely", "scared", "nervous",
        "content", "relieved", "guilty", "ashamed", "confused",
        "hopeless", "worthless", "irritable", "tearful", "panicky",
    ]

    TOPIC_INDICATORS = {
        "relationships": ["partner", "spouse", "marriage", "dating", "boyfriend", "girlfriend",
                          "husband", "wife", "relationship", "breakup", "divorce"],
        "family": ["family", "mother", "father", "parent", "sibling", "brother", "sister",
                   "child", "children", "daughter", "son"],
        "work": ["work", "job", "career", "boss", "coworker", "office", "fired",
                 "promotion", "workplace", "employment"],
        "health": ["health", "sleep", "insomnia", "appetite", "exercise", "pain",
                   "medication", "doctor", "diagnosis", "illness"],
        "trauma": ["trauma", "abuse", "assault", "ptsd", "flashback", "nightmare",
                   "accident", "violence", "neglect"],
        "substance_use": ["alcohol", "drinking", "drugs", "substance", "sober",
                          "relapse", "recovery", "addiction", "using"],
        "self_esteem": ["confidence", "self-esteem", "worthless", "inadequate",
                        "failure", "not good enough", "self-worth"],
        "grief": ["grief", "loss", "death", "died", "mourning", "bereavement",
                  "missing", "funeral"],
    }

    INTERVENTION_MAP = {
        "cbt": "Cognitive Behavioral Therapy techniques",
        "mindfulness": "mindfulness-based interventions",
        "psychoeducation": "psychoeducation",
        "relaxation": "relaxation training",
        "exposure": "exposure-based techniques",
        "behavioral activation": "behavioral activation",
        "motivational interviewing": "motivational interviewing",
        "narrative": "narrative therapy techniques",
        "solution-focused": "solution-focused brief therapy",
        "dbt": "Dialectical Behavior Therapy skills",
    }

    def generate(self, session: Session) -> DAPNote:
        """Generate a DAP note from a therapy session."""
        transcript_lower = session.transcript.lower()

        data = self._extract_data(session, transcript_lower)
        assessment = self._generate_assessment(session, transcript_lower)
        plan = self._generate_plan(session, transcript_lower)

        return DAPNote(
            session_id=session.session_id,
            client_id=session.client_id,
            session_date=session.session_date,
            data=data,
            assessment=assessment,
            plan=plan,
        )

    def _extract_data(self, session: Session, transcript_lower: str) -> str:
        """Extract data section combining subjective and objective information."""
        parts: list[str] = []

        # Session context
        parts.append(
            f"Session #{session.session_number} ({session.duration_minutes} minutes, "
            f"{session.modality}). "
        )

        # Identified emotions
        emotions = [e for e in self.EMOTION_WORDS if e in transcript_lower]
        if emotions:
            parts.append(
                f"Client expressed emotions including: {', '.join(emotions[:6])}. "
            )

        # Identified topics
        topics = self._identify_topics(transcript_lower)
        if topics:
            parts.append(f"Topics discussed: {', '.join(topics)}. ")

        # Client statements - extract key sentences
        key_statements = self._extract_key_statements(session.transcript)
        if key_statements:
            parts.append("Key client statements: " + "; ".join(key_statements[:4]) + ". ")

        # Interventions used
        interventions = self._identify_interventions(transcript_lower)
        if interventions:
            parts.append(
                "Therapeutic interventions utilized: " + ", ".join(interventions) + ". "
            )
        else:
            parts.append(
                "Supportive listening and reflective techniques were utilized. "
            )

        # Behavioral observations
        observations = self._extract_observations(transcript_lower)
        if observations:
            parts.append(" ".join(observations))

        return "".join(parts).strip()

    def _identify_topics(self, transcript_lower: str) -> list[str]:
        """Identify discussion topics from the transcript."""
        found = []
        for topic, keywords in self.TOPIC_INDICATORS.items():
            if any(kw in transcript_lower for kw in keywords):
                found.append(topic.replace("_", " "))
        return found

    def _extract_key_statements(self, transcript: str) -> list[str]:
        """Extract significant client statements."""
        sentences = re.split(r'[.!?]+', transcript)
        key = []
        important_phrases = [
            "i feel", "i think", "i need", "i want", "i can't",
            "i'm afraid", "i realized", "i noticed", "i've been",
            "it hurts", "it's hard", "i wish", "i hope",
        ]
        for sentence in sentences:
            s_lower = sentence.lower().strip()
            if any(p in s_lower for p in important_phrases) and len(s_lower) > 15:
                cleaned = sentence.strip()
                if cleaned and cleaned not in key:
                    key.append(f'"{cleaned}"')
        return key[:5]

    def _identify_interventions(self, transcript_lower: str) -> list[str]:
        """Identify therapeutic interventions mentioned."""
        found = []
        for keyword, description in self.INTERVENTION_MAP.items():
            if keyword in transcript_lower:
                found.append(description)
        return found

    def _extract_observations(self, transcript_lower: str) -> list[str]:
        """Extract behavioral observations."""
        obs: list[str] = []
        if any(w in transcript_lower for w in ["tearful", "crying", "cried", "tears"]):
            obs.append("Client was tearful during portions of the session.")
        if any(w in transcript_lower for w in ["smiled", "laughed", "humor"]):
            obs.append("Client demonstrated positive affect at times.")
        if any(w in transcript_lower for w in ["avoidant", "avoided", "changed the subject"]):
            obs.append("Client exhibited avoidant behavior around certain topics.")
        if any(w in transcript_lower for w in ["insight", "realized", "understood", "awareness"]):
            obs.append("Client demonstrated emerging insight.")
        return obs

    def _generate_assessment(self, session: Session, transcript_lower: str) -> str:
        """Generate clinical assessment."""
        parts: list[str] = []

        # Functional assessment
        if any(w in transcript_lower for w in ["can't function", "can't work", "struggling to"]):
            parts.append("Client's functioning appears impaired in daily activities.")
        elif any(w in transcript_lower for w in ["coping", "managing", "handling"]):
            parts.append("Client demonstrates developing coping capacity.")
        else:
            parts.append("Client's overall functioning is consistent with previous sessions.")

        # Symptom trajectory
        if any(w in transcript_lower for w in ["better", "improved", "progress"]):
            parts.append("Symptom trajectory shows improvement.")
        elif any(w in transcript_lower for w in ["worse", "worsening", "deteriorating"]):
            parts.append("Symptom exacerbation noted; reassessment warranted.")
        else:
            parts.append("Symptom presentation remains stable.")

        # Risk level
        if any(w in transcript_lower for w in ["suicidal", "self-harm", "kill myself"]):
            parts.append("Elevated risk factors identified; safety assessment completed.")
        else:
            parts.append("No acute safety concerns identified at this time.")

        # Treatment engagement
        if any(w in transcript_lower for w in ["homework", "practiced", "tried the"]):
            parts.append("Client engaged with between-session assignments.")

        return " ".join(parts)

    def _generate_plan(self, session: Session, transcript_lower: str) -> str:
        """Generate treatment plan."""
        plans: list[str] = []

        plans.append(f"1. Continue {session.modality} therapy sessions as scheduled.")

        plan_num = 2
        topics = self._identify_topics(transcript_lower)
        if "relationships" in topics or "family" in topics:
            plans.append(
                f"{plan_num}. Explore relational patterns and attachment dynamics."
            )
            plan_num += 1
        if "trauma" in topics:
            plans.append(
                f"{plan_num}. Continue trauma processing at client's pace; "
                f"ensure adequate stabilization."
            )
            plan_num += 1
        if "substance use" in topics:
            plans.append(
                f"{plan_num}. Monitor substance use patterns; "
                f"consider referral for substance abuse evaluation."
            )
            plan_num += 1

        if any(w in transcript_lower for w in ["anxious", "anxiety", "panic"]):
            plans.append(
                f"{plan_num}. Assign between-session practice of anxiety management techniques."
            )
            plan_num += 1
        if any(w in transcript_lower for w in ["depressed", "depression", "sad"]):
            plans.append(
                f"{plan_num}. Implement behavioral activation; "
                f"track mood using daily mood log."
            )
            plan_num += 1

        plans.append(f"{plan_num}. Review progress toward treatment goals next session.")

        return " ".join(plans)
