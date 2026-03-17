"""Data models for therapy session notes."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class NoteFormat(str, Enum):
    """Supported note formats."""

    SOAP = "soap"
    DAP = "dap"
    BIRP = "birp"


class RiskLevel(str, Enum):
    """Risk severity levels."""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    """Categories of risk flags."""

    SUICIDAL_IDEATION = "suicidal_ideation"
    SELF_HARM = "self_harm"
    HOMICIDAL_IDEATION = "homicidal_ideation"
    SUBSTANCE_ABUSE = "substance_abuse"
    PSYCHOSIS = "psychosis"
    ABUSE_NEGLECT = "abuse_neglect"
    EATING_DISORDER = "eating_disorder"
    SEVERE_DEPRESSION = "severe_depression"


class Session(BaseModel):
    """Represents a therapy session."""

    session_id: str = Field(description="Unique session identifier")
    client_id: str = Field(description="Client identifier")
    therapist_id: str = Field(default="THERAPIST001", description="Therapist identifier")
    session_date: datetime = Field(default_factory=datetime.now)
    session_number: int = Field(default=1, ge=1)
    duration_minutes: int = Field(default=50, ge=1)
    transcript: str = Field(description="Session transcript text")
    modality: str = Field(default="individual", description="Session modality")
    presenting_concerns: list[str] = Field(default_factory=list)


class SOAPNote(BaseModel):
    """SOAP format therapy note."""

    session_id: str
    client_id: str
    session_date: datetime = Field(default_factory=datetime.now)
    subjective: str = Field(description="Client's self-reported experiences, feelings, and concerns")
    objective: str = Field(description="Therapist observations of behavior, affect, presentation")
    assessment: str = Field(description="Clinical interpretation, diagnosis considerations, progress")
    plan: str = Field(description="Treatment goals, interventions, next steps")
    diagnosis_codes: list[str] = Field(default_factory=list)
    next_session: Optional[str] = None


class DAPNote(BaseModel):
    """DAP format therapy note."""

    session_id: str
    client_id: str
    session_date: datetime = Field(default_factory=datetime.now)
    data: str = Field(description="All relevant information gathered during the session")
    assessment: str = Field(description="Clinical interpretation and analysis")
    plan: str = Field(description="Future treatment directions and action items")
    diagnosis_codes: list[str] = Field(default_factory=list)
    next_session: Optional[str] = None


class BIRPNote(BaseModel):
    """BIRP format therapy note."""

    session_id: str
    client_id: str
    session_date: datetime = Field(default_factory=datetime.now)
    behavior: str = Field(description="Observable client behaviors and presenting issues")
    intervention: str = Field(description="Therapeutic techniques and interventions used")
    response: str = Field(description="Client's response to interventions")
    plan: str = Field(description="Next steps and future session planning")
    diagnosis_codes: list[str] = Field(default_factory=list)
    next_session: Optional[str] = None


class Theme(BaseModel):
    """A theme or topic identified in a session."""

    name: str = Field(description="Theme name")
    category: str = Field(description="Theme category (e.g., emotional, relational, behavioral)")
    frequency: int = Field(default=1, description="How many times this theme appeared")
    keywords: list[str] = Field(default_factory=list, description="Keywords associated with this theme")
    description: str = Field(default="", description="Brief description of how this theme appeared")
    severity: str = Field(default="moderate", description="Severity or intensity of the theme")


class RiskFlag(BaseModel):
    """A safety concern identified in a session."""

    category: RiskCategory
    level: RiskLevel
    indicator: str = Field(description="The specific text or behavior that triggered this flag")
    context: str = Field(default="", description="Surrounding context for the indicator")
    recommended_action: str = Field(default="", description="Suggested clinical response")
    requires_immediate_action: bool = Field(default=False)


class ProgressEntry(BaseModel):
    """Progress tracking entry across sessions."""

    session_id: str
    session_date: datetime
    session_number: int
    themes: list[Theme] = Field(default_factory=list)
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    mood_rating: Optional[int] = Field(default=None, ge=1, le=10)
    functioning_level: Optional[str] = None
    goals_progress: dict[str, str] = Field(default_factory=dict)
    notes: str = Field(default="")
