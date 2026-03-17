"""SOAP Note Generator - Subjective, Objective, Assessment, Plan."""

from __future__ import annotations

import re
from datetime import datetime

from sessionnotes.models import Session, SOAPNote


class SOAPNoteGenerator:
    """Generate SOAP format therapy notes from session transcripts.

    SOAP notes are the most widely used format in clinical documentation:
    - Subjective: What the client reports
    - Objective: What the therapist observes
    - Assessment: Clinical interpretation
    - Plan: Treatment direction
    """

    # Keywords for extracting subjective content
    SUBJECTIVE_INDICATORS = [
        "i feel", "i felt", "i think", "i thought", "i've been",
        "i am", "i'm", "i was", "i have", "i had",
        "it makes me", "it made me", "worried about", "struggling with",
        "concerned about", "afraid of", "upset about", "happy about",
        "stressed", "anxious", "depressed", "angry", "sad", "hopeless",
        "frustrated", "overwhelmed", "lonely", "scared", "nervous",
        "can't sleep", "not eating", "eating too much", "drinking",
        "my relationship", "my partner", "my family", "my job", "my boss",
    ]

    # Keywords for objective observations
    OBJECTIVE_INDICATORS = [
        "appeared", "presented", "observed", "displayed", "demonstrated",
        "affect", "mood", "grooming", "eye contact", "speech",
        "cooperative", "engaged", "withdrawn", "agitated", "tearful",
        "well-groomed", "disheveled", "alert", "oriented", "coherent",
        "psychomotor", "fidgeting", "restless", "calm", "flat affect",
    ]

    # Mood/affect descriptors
    MOOD_DESCRIPTORS = {
        "positive": ["happy", "hopeful", "optimistic", "content", "relaxed", "calm", "motivated"],
        "negative": ["sad", "depressed", "anxious", "angry", "frustrated", "hopeless", "tearful"],
        "neutral": ["stable", "euthymic", "appropriate", "flat", "restricted"],
    }

    # Intervention keywords
    INTERVENTION_KEYWORDS = [
        "cbt", "cognitive behavioral", "mindfulness", "relaxation",
        "exposure", "psychoeducation", "role play", "journaling",
        "breathing", "grounding", "reframing", "cognitive restructuring",
        "behavioral activation", "motivational interviewing", "emdr",
        "dialectical", "solution-focused", "narrative", "acceptance",
    ]

    def generate(self, session: Session) -> SOAPNote:
        """Generate a SOAP note from a therapy session."""
        transcript_lower = session.transcript.lower()

        subjective = self._extract_subjective(session.transcript, transcript_lower)
        objective = self._extract_objective(session.transcript, transcript_lower)
        assessment = self._generate_assessment(
            session, transcript_lower, subjective, objective
        )
        plan = self._generate_plan(session, transcript_lower, assessment)

        return SOAPNote(
            session_id=session.session_id,
            client_id=session.client_id,
            session_date=session.session_date,
            subjective=subjective,
            objective=objective,
            assessment=assessment,
            plan=plan,
        )

    def _extract_subjective(self, transcript: str, transcript_lower: str) -> str:
        """Extract subjective content - client's self-reported experiences."""
        findings: list[str] = []
        sentences = re.split(r'[.!?]+', transcript)

        reported_feelings: list[str] = []
        reported_concerns: list[str] = []
        reported_symptoms: list[str] = []

        symptom_words = [
            "can't sleep", "insomnia", "nightmares", "appetite", "eating",
            "fatigue", "tired", "energy", "concentration", "panic",
            "headache", "pain", "nausea",
        ]

        for sentence in sentences:
            s_lower = sentence.lower().strip()
            if not s_lower:
                continue

            for indicator in self.SUBJECTIVE_INDICATORS:
                if indicator in s_lower:
                    cleaned = sentence.strip()
                    if any(w in s_lower for w in ["feel", "felt", "emotion", "mood"]):
                        reported_feelings.append(cleaned)
                    elif any(w in s_lower for w in ["worried", "concerned", "afraid", "struggling"]):
                        reported_concerns.append(cleaned)
                    break

            for symptom in symptom_words:
                if symptom in s_lower:
                    reported_symptoms.append(sentence.strip())
                    break

        if reported_feelings:
            findings.append(
                "Client reported the following emotional experiences: "
                + "; ".join(dict.fromkeys(reported_feelings[:5]))
                + "."
            )
        if reported_concerns:
            findings.append(
                "Client expressed concerns regarding: "
                + "; ".join(dict.fromkeys(reported_concerns[:5]))
                + "."
            )
        if reported_symptoms:
            findings.append(
                "Client reported symptoms including: "
                + "; ".join(dict.fromkeys(reported_symptoms[:5]))
                + "."
            )

        if not findings:
            findings.append(
                "Client engaged in session and discussed presenting concerns. "
                "Specific self-reported experiences were explored during the session."
            )

        return " ".join(findings)

    def _extract_objective(self, transcript: str, transcript_lower: str) -> str:
        """Extract objective content - therapist observations."""
        observations: list[str] = []

        # Determine affect
        affect = self._assess_affect(transcript_lower)
        observations.append(f"Client's affect appeared {affect}.")

        # Check engagement level
        engagement = self._assess_engagement(transcript_lower)
        observations.append(f"Client was {engagement} during the session.")

        # Check for behavioral observations
        if any(w in transcript_lower for w in ["crying", "tearful", "tears", "cried"]):
            observations.append("Client became tearful during session.")
        if any(w in transcript_lower for w in ["agitated", "restless", "fidgeting", "pacing"]):
            observations.append("Psychomotor agitation was observed.")
        if any(w in transcript_lower for w in ["calm", "relaxed", "composed"]):
            observations.append("Client presented with calm demeanor.")

        # Speech and thought
        if any(w in transcript_lower for w in ["racing thoughts", "rapid speech", "pressured"]):
            observations.append("Speech was noted to be pressured or rapid.")
        if any(w in transcript_lower for w in ["slow", "lethargic", "flat"]):
            observations.append("Psychomotor retardation was noted.")

        observations.append("Thought process was linear and goal-directed.")
        observations.append("Client was alert and oriented.")

        return " ".join(observations)

    def _assess_affect(self, transcript_lower: str) -> str:
        """Assess the client's overall affect from the transcript."""
        pos_count = sum(1 for w in self.MOOD_DESCRIPTORS["positive"] if w in transcript_lower)
        neg_count = sum(1 for w in self.MOOD_DESCRIPTORS["negative"] if w in transcript_lower)

        if neg_count > pos_count + 2:
            return "constricted with depressed mood"
        elif neg_count > pos_count:
            return "mildly dysphoric"
        elif pos_count > neg_count + 2:
            return "bright and expansive"
        elif pos_count > neg_count:
            return "pleasant and appropriate"
        return "congruent with stated mood"

    def _assess_engagement(self, transcript_lower: str) -> str:
        """Assess client engagement level."""
        if any(w in transcript_lower for w in ["refused", "resistant", "unwilling", "silent"]):
            return "minimally engaged"
        if any(w in transcript_lower for w in ["eager", "enthusiastic", "motivated", "open"]):
            return "highly engaged and cooperative"
        return "cooperative and engaged"

    def _generate_assessment(
        self,
        session: Session,
        transcript_lower: str,
        subjective: str,
        objective: str,
    ) -> str:
        """Generate clinical assessment."""
        parts: list[str] = []

        # Overall clinical impression
        if any(w in transcript_lower for w in ["hopeless", "suicidal", "end my life", "worthless"]):
            parts.append(
                "Client presents with significant depressive symptomatology "
                "warranting close monitoring."
            )
        elif any(w in transcript_lower for w in ["anxious", "panic", "worry", "nervous"]):
            parts.append(
                "Client presents with anxiety-related symptoms impacting daily functioning."
            )
        elif any(w in transcript_lower for w in ["angry", "rage", "furious"]):
            parts.append(
                "Client presents with anger management concerns requiring targeted intervention."
            )
        else:
            parts.append(
                "Client presents with concerns consistent with presenting problems."
            )

        # Progress assessment
        if any(w in transcript_lower for w in ["better", "improved", "progress", "coping"]):
            parts.append("Some progress noted toward treatment goals.")
        elif any(w in transcript_lower for w in ["worse", "deteriorat", "declining"]):
            parts.append(
                "Symptom exacerbation noted; treatment plan may need adjustment."
            )
        else:
            parts.append("Client continues to work on treatment goals.")

        # Presenting concerns
        if session.presenting_concerns:
            parts.append(
                f"Presenting concerns include: {', '.join(session.presenting_concerns)}."
            )

        return " ".join(parts)

    def _generate_plan(
        self, session: Session, transcript_lower: str, assessment: str
    ) -> str:
        """Generate treatment plan."""
        plans: list[str] = []

        plans.append(f"Continue {session.modality} therapy sessions.")

        # Suggest interventions based on content
        if any(w in transcript_lower for w in ["anxious", "anxiety", "panic", "worry"]):
            plans.append(
                "Incorporate relaxation training and cognitive restructuring "
                "for anxiety management."
            )
        if any(w in transcript_lower for w in ["depressed", "sad", "hopeless", "worthless"]):
            plans.append(
                "Implement behavioral activation strategies. "
                "Monitor mood and assess need for psychiatric referral."
            )
        if any(w in transcript_lower for w in ["anger", "angry", "rage"]):
            plans.append(
                "Introduce anger management techniques including "
                "identification of triggers and de-escalation strategies."
            )
        if any(w in transcript_lower for w in ["relationship", "partner", "marriage", "family"]):
            plans.append("Explore relational dynamics and communication patterns.")
        if any(w in transcript_lower for w in ["trauma", "ptsd", "abuse", "assault"]):
            plans.append(
                "Continue trauma-focused work with appropriate pacing. "
                "Consider EMDR or prolonged exposure when client is ready."
            )
        if any(w in transcript_lower for w in ["suicidal", "self-harm", "hurt myself"]):
            plans.append(
                "SAFETY PLAN: Review and update safety plan. "
                "Assess need for higher level of care. "
                "Ensure emergency contacts are current."
            )

        plans.append(f"Next session scheduled for {session.duration_minutes}-minute session.")

        return " ".join(plans)
