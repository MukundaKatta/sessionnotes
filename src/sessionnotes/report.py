"""Rich-formatted reports for therapy session notes."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from sessionnotes.models import (
    BIRPNote,
    DAPNote,
    ProgressEntry,
    RiskFlag,
    RiskLevel,
    SOAPNote,
    Theme,
)


class ReportGenerator:
    """Generate rich-formatted clinical reports."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def display_soap_note(self, note: SOAPNote) -> None:
        """Display a SOAP note with rich formatting."""
        self.console.print()
        self.console.print(
            Panel(
                f"[bold]Client:[/bold] {note.client_id}  |  "
                f"[bold]Session:[/bold] {note.session_id}  |  "
                f"[bold]Date:[/bold] {note.session_date.strftime('%Y-%m-%d')}",
                title="[bold blue]SOAP Note[/bold blue]",
                border_style="blue",
            )
        )

        sections = [
            ("S - Subjective", note.subjective, "green"),
            ("O - Objective", note.objective, "yellow"),
            ("A - Assessment", note.assessment, "cyan"),
            ("P - Plan", note.plan, "magenta"),
        ]

        for title, content, color in sections:
            self.console.print(
                Panel(content, title=f"[bold {color}]{title}[/bold {color}]", border_style=color)
            )

        if note.diagnosis_codes:
            self.console.print(
                f"[dim]Diagnosis Codes: {', '.join(note.diagnosis_codes)}[/dim]"
            )
        self.console.print()

    def display_dap_note(self, note: DAPNote) -> None:
        """Display a DAP note with rich formatting."""
        self.console.print()
        self.console.print(
            Panel(
                f"[bold]Client:[/bold] {note.client_id}  |  "
                f"[bold]Session:[/bold] {note.session_id}  |  "
                f"[bold]Date:[/bold] {note.session_date.strftime('%Y-%m-%d')}",
                title="[bold blue]DAP Note[/bold blue]",
                border_style="blue",
            )
        )

        sections = [
            ("D - Data", note.data, "green"),
            ("A - Assessment", note.assessment, "yellow"),
            ("P - Plan", note.plan, "magenta"),
        ]

        for title, content, color in sections:
            self.console.print(
                Panel(content, title=f"[bold {color}]{title}[/bold {color}]", border_style=color)
            )
        self.console.print()

    def display_birp_note(self, note: BIRPNote) -> None:
        """Display a BIRP note with rich formatting."""
        self.console.print()
        self.console.print(
            Panel(
                f"[bold]Client:[/bold] {note.client_id}  |  "
                f"[bold]Session:[/bold] {note.session_id}  |  "
                f"[bold]Date:[/bold] {note.session_date.strftime('%Y-%m-%d')}",
                title="[bold blue]BIRP Note[/bold blue]",
                border_style="blue",
            )
        )

        sections = [
            ("B - Behavior", note.behavior, "green"),
            ("I - Intervention", note.intervention, "yellow"),
            ("R - Response", note.response, "cyan"),
            ("P - Plan", note.plan, "magenta"),
        ]

        for title, content, color in sections:
            self.console.print(
                Panel(content, title=f"[bold {color}]{title}[/bold {color}]", border_style=color)
            )
        self.console.print()

    def display_themes(self, themes: list[Theme]) -> None:
        """Display extracted themes in a table."""
        table = Table(title="Session Themes", border_style="blue")
        table.add_column("Theme", style="bold")
        table.add_column("Category", style="cyan")
        table.add_column("Frequency", justify="center")
        table.add_column("Severity", justify="center")
        table.add_column("Keywords")

        severity_colors = {
            "high": "red",
            "moderate": "yellow",
            "mild": "green",
            "minimal": "dim",
        }

        for theme in themes:
            color = severity_colors.get(theme.severity, "white")
            table.add_row(
                theme.name,
                theme.category,
                str(theme.frequency),
                Text(theme.severity, style=color),
                ", ".join(theme.keywords[:5]),
            )

        self.console.print()
        self.console.print(table)
        self.console.print()

    def display_risk_flags(self, flags: list[RiskFlag]) -> None:
        """Display risk screening results."""
        if not flags:
            self.console.print(
                Panel(
                    "[green]No significant risk factors identified.[/green]",
                    title="[bold green]Risk Screening Results[/bold green]",
                    border_style="green",
                )
            )
            return

        level_styles = {
            RiskLevel.CRITICAL: ("bold white on red", "CRITICAL"),
            RiskLevel.HIGH: ("bold red", "HIGH"),
            RiskLevel.MODERATE: ("bold yellow", "MODERATE"),
            RiskLevel.LOW: ("bold green", "LOW"),
        }

        self.console.print()
        self.console.print(
            Panel(
                f"[bold red]{len(flags)} risk factor(s) identified[/bold red]",
                title="[bold red]Risk Screening Results[/bold red]",
                border_style="red",
            )
        )

        for flag in flags:
            style, label = level_styles.get(flag.level, ("white", "UNKNOWN"))
            self.console.print(
                Panel(
                    f"[bold]Category:[/bold] {flag.category.value.replace('_', ' ').title()}\n"
                    f"[bold]Level:[/bold] [{style}]{label}[/{style}]\n"
                    f"[bold]Indicator:[/bold] {flag.indicator}\n"
                    f"[bold]Context:[/bold] {flag.context}\n\n"
                    f"[bold]Recommended Action:[/bold] {flag.recommended_action}",
                    border_style="red" if flag.requires_immediate_action else "yellow",
                )
            )

        self.console.print()

    def display_progress(self, entries: list[ProgressEntry]) -> None:
        """Display progress tracking across sessions."""
        table = Table(title="Progress Tracking", border_style="blue")
        table.add_column("Session #", justify="center")
        table.add_column("Date")
        table.add_column("Mood (1-10)", justify="center")
        table.add_column("Functioning")
        table.add_column("Risk Flags", justify="center")
        table.add_column("Top Themes")

        for entry in entries:
            mood_str = str(entry.mood_rating) if entry.mood_rating else "N/A"
            if entry.mood_rating:
                if entry.mood_rating >= 7:
                    mood_str = f"[green]{mood_str}[/green]"
                elif entry.mood_rating <= 3:
                    mood_str = f"[red]{mood_str}[/red]"
                else:
                    mood_str = f"[yellow]{mood_str}[/yellow]"

            risk_count = len(entry.risk_flags)
            risk_str = (
                f"[red]{risk_count}[/red]" if risk_count > 0 else "[green]0[/green]"
            )

            top_themes = ", ".join(t.name for t in entry.themes[:3])

            table.add_row(
                str(entry.session_number),
                entry.session_date.strftime("%Y-%m-%d"),
                mood_str,
                entry.functioning_level or "N/A",
                risk_str,
                top_themes or "None identified",
            )

        self.console.print()
        self.console.print(table)
        self.console.print()
