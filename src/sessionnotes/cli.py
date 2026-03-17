"""Command-line interface for SessionNotes."""

from __future__ import annotations

import click
from rich.console import Console

from sessionnotes.analyzer.progress import ProgressTracker
from sessionnotes.analyzer.risk import RiskScreener
from sessionnotes.analyzer.themes import ThemeExtractor
from sessionnotes.generator.birp import BIRPNoteGenerator
from sessionnotes.generator.dap import DAPNoteGenerator
from sessionnotes.generator.soap import SOAPNoteGenerator
from sessionnotes.models import NoteFormat, Session
from sessionnotes.report import ReportGenerator

console = Console()


SAMPLE_TRANSCRIPT = (
    "Client arrived on time and appeared well-groomed but fatigued. "
    "Client reported feeling increasingly anxious over the past week, "
    "particularly related to work deadlines. Client stated 'I feel like "
    "I can't keep up and everyone is going to find out I'm a fraud.' "
    "Client described difficulty sleeping, with racing thoughts at night. "
    "Client mentioned that the breathing exercises discussed last session "
    "have been somewhat helpful. Client practiced the 4-7-8 breathing "
    "technique during session and reported feeling calmer afterward. "
    "Client expressed motivation to continue working on anxiety management "
    "and agreed to maintain a worry journal this week. "
    "Client denied any suicidal ideation or self-harm urges."
)


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """SessionNotes - AI Therapy Note Generator.

    Generate structured clinical notes from therapy session transcripts.
    """
    pass


@cli.command()
@click.option(
    "--format", "note_format",
    type=click.Choice(["soap", "dap", "birp"], case_sensitive=False),
    default="soap",
    help="Note format to generate",
)
@click.option("--transcript", "-t", default=None, help="Session transcript text")
@click.option("--client-id", "-c", default="CLIENT001", help="Client identifier")
@click.option("--session-id", "-s", default="SESSION001", help="Session identifier")
@click.option("--session-number", "-n", default=1, type=int, help="Session number")
@click.option("--duration", "-d", default=50, type=int, help="Session duration in minutes")
@click.option("--modality", "-m", default="individual", help="Session modality")
def generate(
    note_format: str,
    transcript: str | None,
    client_id: str,
    session_id: str,
    session_number: int,
    duration: int,
    modality: str,
) -> None:
    """Generate a therapy note from a session transcript."""
    if transcript is None:
        transcript = SAMPLE_TRANSCRIPT
        console.print("[dim]Using sample transcript (use --transcript to provide your own)[/dim]")

    session = Session(
        session_id=session_id,
        client_id=client_id,
        session_number=session_number,
        duration_minutes=duration,
        transcript=transcript,
        modality=modality,
    )

    report = ReportGenerator(console)
    fmt = NoteFormat(note_format.lower())

    if fmt == NoteFormat.SOAP:
        generator = SOAPNoteGenerator()
        note = generator.generate(session)
        report.display_soap_note(note)
    elif fmt == NoteFormat.DAP:
        generator = DAPNoteGenerator()
        note = generator.generate(session)
        report.display_dap_note(note)
    elif fmt == NoteFormat.BIRP:
        generator = BIRPNoteGenerator()
        note = generator.generate(session)
        report.display_birp_note(note)


@cli.group()
def analyze() -> None:
    """Analyze session transcripts."""
    pass


@analyze.command()
@click.option("--transcript", "-t", default=None, help="Session transcript text")
@click.option("--max-themes", default=10, type=int, help="Maximum themes to display")
def themes(transcript: str | None, max_themes: int) -> None:
    """Extract themes from a session transcript."""
    if transcript is None:
        transcript = SAMPLE_TRANSCRIPT
        console.print("[dim]Using sample transcript[/dim]")

    session = Session(
        session_id="SESSION001",
        client_id="CLIENT001",
        transcript=transcript,
    )

    extractor = ThemeExtractor()
    found_themes = extractor.extract(session)[:max_themes]

    report = ReportGenerator(console)
    report.display_themes(found_themes)


@analyze.command()
@click.option("--transcript", "-t", default=None, help="Session transcript text")
def risk(transcript: str | None) -> None:
    """Screen a transcript for safety concerns."""
    if transcript is None:
        transcript = SAMPLE_TRANSCRIPT
        console.print("[dim]Using sample transcript[/dim]")

    session = Session(
        session_id="SESSION001",
        client_id="CLIENT001",
        transcript=transcript,
    )

    screener = RiskScreener()
    flags = screener.screen(session)
    overall_level = screener.get_overall_risk_level(session)

    report = ReportGenerator(console)
    report.display_risk_flags(flags)

    console.print(f"[bold]Overall Risk Level:[/bold] {overall_level.value}")


@cli.command()
@click.option("--client-id", "-c", default="CLIENT001", help="Client identifier")
def report(client_id: str) -> None:
    """Generate a progress report using sample multi-session data."""
    sessions = [
        Session(
            session_id=f"S{i:03d}",
            client_id=client_id,
            session_number=i,
            transcript=t,
        )
        for i, t in enumerate(
            [
                "Client reported feeling very depressed and hopeless. "
                "Can't get out of bed most days. No motivation. Crying frequently. "
                "Struggling at work. Relationship with partner is strained.",

                "Client reported slight improvement in mood. Still feeling sad but "
                "managed to go to work this week. Practiced breathing exercises. "
                "Discussed coping strategies for anxiety. Client is motivated to try.",

                "Client reported feeling better. Using coping skills learned in therapy. "
                "Improved relationship communication with partner. Sleep has improved. "
                "Client expressed hopeful outlook. Progress toward treatment goals noted.",
            ],
            start=1,
        )
    ]

    tracker = ProgressTracker()
    entries = tracker.track_progress(sessions)
    trajectory = tracker.get_trajectory(sessions)

    rpt = ReportGenerator(console)
    rpt.display_progress(entries)

    console.print(
        Panel(
            f"[bold]Mood Trend:[/bold] {trajectory['mood_trend']}\n"
            f"[bold]Risk Trend:[/bold] {trajectory['risk_trend']}\n"
            f"[bold]Recurring Themes:[/bold] {', '.join(trajectory['recurring_themes'][:5])}\n"
            f"[bold]Overall Progress:[/bold] {trajectory['overall_progress']}",
            title="[bold blue]Treatment Trajectory[/bold blue]",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    cli()
