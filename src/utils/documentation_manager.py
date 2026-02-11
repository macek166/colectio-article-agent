"""Documentation Manager for tracking system events and problems."""

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field


class DocumentationEntry(BaseModel):
    """Pydantic model for documentation entry."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event: str = Field(..., min_length=1)
    details: str = Field(..., min_length=1)


class ProblemEntry(BaseModel):
    """Pydantic model for problem entry."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    issue: str = Field(..., min_length=1)
    status: Literal["active", "resolved", "blocked"]
    details: str = Field(..., min_length=1)


class DocumentationManager:
    """Manages DOCUMENTATION.md and PROBLEMS.md files."""

    def __init__(self, docs_dir: str = "docs") -> None:
        """Initialize documentation manager.

        Args:
            docs_dir: Directory path for documentation files
        """
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        self.documentation_file = self.docs_dir / "DOCUMENTATION.md"
        self.problems_file = self.docs_dir / "PROBLEMS.md"

        # Create files if they don't exist
        self._initialize_documentation_file()
        self._initialize_problems_file()

    def _initialize_documentation_file(self) -> None:
        """Create DOCUMENTATION.md if it doesn't exist."""
        if not self.documentation_file.exists():
            with open(self.documentation_file, 'w', encoding='utf-8') as f:
                f.write("# System Documentation\n\n")
                f.write("This file tracks significant events and architectural decisions.\n\n")
                f.write("---\n\n")

    def _initialize_problems_file(self) -> None:
        """Create PROBLEMS.md if it doesn't exist."""
        if not self.problems_file.exists():
            with open(self.problems_file, 'w', encoding='utf-8') as f:
                f.write("# System Problems\n\n")
                f.write("This file tracks active issues, errors, and their resolution status.\n\n")
                f.write("---\n\n")

    def log_event(self, event: str, details: str) -> None:
        """Append event to DOCUMENTATION.md with timestamp.

        Args:
            event: Brief description of the event
            details: Detailed information about the event
        """
        entry = DocumentationEntry(event=event, details=details)

        with open(self.documentation_file, 'a', encoding='utf-8') as f:
            f.write(f"## {entry.event}\n")
            # Type ignore needed due to Pydantic Field type inference issue
            f.write(f"**Timestamp:** {entry.timestamp.isoformat()}\n\n")  # type: ignore[attr-defined]
            f.write(f"{entry.details}\n\n")
            f.write("---\n\n")

    def log_problem(self, issue: str, status: str, details: str) -> None:
        """Log problem to PROBLEMS.md with status.

        Args:
            issue: Brief description of the problem
            status: Status of the problem (active, resolved, blocked)
            details: Detailed information about the problem
        """
        entry = ProblemEntry(issue=issue, status=status, details=details)

        with open(self.problems_file, 'a', encoding='utf-8') as f:
            f.write(f"## {entry.issue}\n")
            # Type ignore needed due to Pydantic Field type inference issue
            f.write(f"**Timestamp:** {entry.timestamp.isoformat()}\n")  # type: ignore[attr-defined]
            f.write(f"**Status:** {entry.status}\n\n")
            f.write(f"{entry.details}\n\n")
            f.write("---\n\n")

    def update_problem_status(self, issue: str, new_status: str) -> None:
        """Update problem status in PROBLEMS.md.

        Args:
            issue: The issue description to find and update
            new_status: New status value (active, resolved, blocked)
        """
        # Validate status
        if new_status not in ["active", "resolved", "blocked"]:
            raise ValueError(f"Invalid status: {new_status}")

        if not self.problems_file.exists():
            return

        # Read the entire file
        with open(self.problems_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find and update the status for the matching issue
        lines = content.split('\n')
        updated_lines = []
        in_target_section = False

        for line in lines:
            if line.startswith('## ') and issue in line:
                in_target_section = True
                updated_lines.append(line)
            elif in_target_section and line.startswith('**Status:**'):
                updated_lines.append(f"**Status:** {new_status}")
                in_target_section = False
            else:
                updated_lines.append(line)

        # Write back the updated content
        with open(self.problems_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))

    def regenerate_agent_structure(self) -> bool:
        """Regenerate AGENT_STRUCTURE.md by running the generation script.

        This method automatically updates the agent structure documentation
        when system changes occur.

        Returns:
            True if regeneration was successful, False otherwise
        """
        try:
            # Find the project root (parent of docs directory)
            project_root = self.docs_dir.parent
            script_path = project_root / "scripts" / "generate_agent_structure.py"

            if not script_path.exists():
                self.log_problem(
                    issue="Agent structure script not found",
                    status="active",
                    details=f"Could not find {script_path}"
                )
                return False

            # Run the generation script
            result = subprocess.run(
                ["python", str(script_path)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                self.log_event(
                    event="Agent Structure Documentation Regenerated",
                    details="Successfully regenerated AGENT_STRUCTURE.md with updated diagrams"
                )
                return True

            self.log_problem(
                issue="Agent structure regeneration failed",
                status="active",
                details=f"Script exited with code {result.returncode}\n"
                       f"Error: {result.stderr}"
            )
            return False

        except Exception as e:
            self.log_problem(
                issue="Agent structure regeneration error",
                status="active",
                details=f"Exception during regeneration: {str(e)}"
            )
            return False
