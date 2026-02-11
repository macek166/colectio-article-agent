"""
Documentation generator utility for automatic AGENT_STRUCTURE.md updates.

This module provides functionality to regenerate the AGENT_STRUCTURE.md
documentation file whenever system changes occur.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


class DocumentationGenerator:
    """Manages automatic generation of system documentation."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the documentation generator.

        Args:
            project_root: Path to project root directory. If None, auto-detect.
        """
        if project_root is None:
            # Auto-detect project root (go up from this file)
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)

        self.script_path = self.project_root / "scripts" / "generate_agent_structure.py"
        self.docs_dir = self.project_root / "docs"
        self.output_file = self.docs_dir / "AGENT_STRUCTURE.md"

    def generate(self) -> bool:
        """
        Generate or regenerate the AGENT_STRUCTURE.md documentation.

        Returns:
            bool: True if generation succeeded, False otherwise
        """
        try:
            # Ensure the script exists
            if not self.script_path.exists():
                print(f"Error: Script not found at {self.script_path}")
                return False

            # Run the generation script
            result = subprocess.run(
                [sys.executable, str(self.script_path)],
                capture_output=True,
                text=True,
                check=True
            )

            # Check if output file was created
            if self.output_file.exists():
                print(f"[OK] Successfully generated {self.output_file}")
                return True
            else:
                print(f"Error: Output file not created at {self.output_file}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"Error running generation script: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def verify_exists(self) -> bool:
        """
        Check if AGENT_STRUCTURE.md exists.

        Returns:
            bool: True if file exists, False otherwise
        """
        return self.output_file.exists()

    def get_last_modified(self) -> Optional[float]:
        """
        Get the last modification timestamp of AGENT_STRUCTURE.md.

        Returns:
            float: Timestamp of last modification, or None if file doesn't exist
        """
        if self.output_file.exists():
            return self.output_file.stat().st_mtime
        return None

    def regenerate_if_needed(self, force: bool = False) -> bool:
        """
        Regenerate documentation if needed or forced.

        Args:
            force: If True, regenerate regardless of current state

        Returns:
            bool: True if regeneration occurred and succeeded
        """
        if force or not self.verify_exists():
            print("Regenerating AGENT_STRUCTURE.md...")
            return self.generate()
        else:
            print("AGENT_STRUCTURE.md already exists. Use force=True to regenerate.")
            return True


def regenerate_documentation(force: bool = False) -> bool:
    """
    Convenience function to regenerate documentation.

    Args:
        force: If True, regenerate regardless of current state

    Returns:
        bool: True if successful
    """
    generator = DocumentationGenerator()
    return generator.regenerate_if_needed(force=force)


if __name__ == "__main__":
    # Allow running this module directly to regenerate docs
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate or regenerate AGENT_STRUCTURE.md documentation"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if file exists"
    )

    args = parser.parse_args()

    success = regenerate_documentation(force=args.force)
    sys.exit(0 if success else 1)
