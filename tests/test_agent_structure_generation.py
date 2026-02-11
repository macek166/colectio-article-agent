"""Tests for agent structure documentation generation."""

import subprocess
from pathlib import Path
import pytest


def test_generate_agent_structure_script_exists():
    """Test that the generation script exists."""
    script_path = Path("scripts/generate_agent_structure.py")
    assert script_path.exists(), "Generation script should exist"


def test_generate_agent_structure_runs_successfully():
    """Test that the generation script runs without errors."""
    result = subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        capture_output=True,
        text=True,
        check=False
    )
    
    assert result.returncode == 0, f"Script should exit successfully: {result.stderr}"
    assert "[OK] Generated" in result.stdout, "Script should report success"


def test_agent_structure_file_created():
    """Test that AGENT_STRUCTURE.md is created."""
    # Run the generation script
    subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        check=True
    )
    
    # Check that the file exists
    output_file = Path("docs/AGENT_STRUCTURE.md")
    assert output_file.exists(), "AGENT_STRUCTURE.md should be created"


def test_agent_structure_contains_required_sections():
    """Test that AGENT_STRUCTURE.md contains all required sections."""
    # Run the generation script
    subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        check=True
    )
    
    # Read the generated file
    output_file = Path("docs/AGENT_STRUCTURE.md")
    content = output_file.read_text(encoding="utf-8")
    
    # Check for required sections
    required_sections = [
        "# Trading Card Content Generator - Agent Structure",
        "## Overview",
        "## System Architecture",
        "## Two-Phase Workflow Sequence",
        "## Data Flow",
        "## Two-Phase Orchestration Workflow",
        "## Agent Details",
        "### Five Specialized Agents",
        "#### 1. Strategist Agent",
        "#### 2. Researcher Agent",
        "#### 3. Writer Agent",
        "#### 4. Editor Agent",
        "#### 5. Archivist Agent",
        "## Integration Details",
        "### Neon Database via Kiro Power",
        "### Context7 MCP Integration",
        "### SEO Tools Integration",
        "## Category-Specific Web Sources",
        "### Pokémon Cards Sources",
        "### Hockey Cards Sources",
        "### Soccer Cards Sources",
        "## Error Handling and Retry Logic",
        "## Configuration",
        "## Technology Stack",
        "## Data Models",
        "## Database Schema",
    ]
    
    for section in required_sections:
        assert section in content, f"Section '{section}' should be present"


def test_agent_structure_contains_mermaid_diagrams():
    """Test that AGENT_STRUCTURE.md contains Mermaid diagrams."""
    # Run the generation script
    subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        check=True
    )
    
    # Read the generated file
    output_file = Path("docs/AGENT_STRUCTURE.md")
    content = output_file.read_text(encoding="utf-8")
    
    # Check for Mermaid diagrams
    assert "```mermaid" in content, "Should contain Mermaid diagrams"
    assert "graph TB" in content, "Should contain system architecture diagram"
    assert "sequenceDiagram" in content, "Should contain sequence diagram"
    assert "graph LR" in content, "Should contain data flow diagram"


def test_agent_structure_shows_all_five_agents():
    """Test that all five agents are documented."""
    # Run the generation script
    subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        check=True
    )
    
    # Read the generated file
    output_file = Path("docs/AGENT_STRUCTURE.md")
    content = output_file.read_text(encoding="utf-8")
    
    # Check for all five agents
    agents = [
        "Strategist Agent",
        "Researcher Agent",
        "Writer Agent",
        "Editor Agent",
        "Archivist Agent"
    ]
    
    for agent in agents:
        assert agent in content, f"Agent '{agent}' should be documented"


def test_agent_structure_shows_two_phase_orchestration():
    """Test that two-phase orchestration is documented."""
    # Run the generation script
    subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        check=True
    )
    
    # Read the generated file
    output_file = Path("docs/AGENT_STRUCTURE.md")
    content = output_file.read_text(encoding="utf-8")
    
    # Check for two-phase workflow
    assert "Strategy Phase" in content, "Strategy Phase should be documented"
    assert "Execution Phase" in content, "Execution Phase should be documented"
    assert "Topic Generation" in content, "Topic generation should be documented"
    assert "Sequential Article Creation" in content, "Sequential processing should be documented"


def test_agent_structure_shows_neon_integration():
    """Test that Neon database integration via Kiro Power is documented."""
    # Run the generation script
    subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        check=True
    )
    
    # Read the generated file
    output_file = Path("docs/AGENT_STRUCTURE.md")
    content = output_file.read_text(encoding="utf-8")
    
    # Check for Neon and Kiro Power integration
    assert "Neon" in content, "Neon database should be documented"
    assert "Kiro Power" in content, "Kiro Power should be documented"
    assert "PostgreSQL" in content, "PostgreSQL should be mentioned"


def test_agent_structure_shows_context7_integration():
    """Test that Context7 MCP integration is documented."""
    # Run the generation script
    subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        check=True
    )
    
    # Read the generated file
    output_file = Path("docs/AGENT_STRUCTURE.md")
    content = output_file.read_text(encoding="utf-8")
    
    # Check for Context7 MCP
    assert "Context7 MCP" in content, "Context7 MCP should be documented"
    assert "Library Documentation" in content, "Library documentation should be mentioned"


def test_agent_structure_shows_category_sources():
    """Test that category-specific web sources are documented."""
    # Run the generation script
    subprocess.run(
        ["python", "scripts/generate_agent_structure.py"],
        check=True
    )
    
    # Read the generated file
    output_file = Path("docs/AGENT_STRUCTURE.md")
    content = output_file.read_text(encoding="utf-8")
    
    # Check for category sources
    assert "Pokémon Cards Sources" in content or "Pokemon Cards Sources" in content
    assert "Hockey Cards Sources" in content
    assert "Soccer Cards Sources" in content
    
    # Check for specific sources
    assert "eBay" in content
    assert "Cardmarket" in content or "TCGplayer" in content
    assert "Beckett" in content


def test_documentation_manager_regenerate_method():
    """Test that DocumentationManager can regenerate agent structure."""
    from src.utils.documentation_manager import DocumentationManager
    
    dm = DocumentationManager()
    result = dm.regenerate_agent_structure()
    
    assert result is True, "Regeneration should succeed"
    
    # Check that the file was updated
    output_file = Path("docs/AGENT_STRUCTURE.md")
    assert output_file.exists(), "AGENT_STRUCTURE.md should exist after regeneration"


def test_documentation_manager_logs_regeneration():
    """Test that regeneration is logged to DOCUMENTATION.md."""
    from src.utils.documentation_manager import DocumentationManager
    
    dm = DocumentationManager()
    dm.regenerate_agent_structure()
    
    # Check that the event was logged
    doc_file = Path("docs/DOCUMENTATION.md")
    content = doc_file.read_text(encoding="utf-8")
    
    assert "Agent Structure Documentation Regenerated" in content, \
        "Regeneration should be logged"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
