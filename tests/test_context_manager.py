"""
Unit tests for Context Manager.

Tests the ContextManager class for storing, retrieving, and managing agent outputs.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.utils.context_manager import ContextManager
from src.models.agent_output import AgentOutput


class TestContextManagerInitialization:
    """Test ContextManager initialization."""
    
    def test_context_manager_initializes_empty(self):
        """Test that ContextManager initializes with empty context."""
        manager = ContextManager()
        assert manager.get_full_history() == []
        assert manager.get_context() == {}
    
    def test_context_manager_multiple_instances_isolated(self):
        """Test that multiple ContextManager instances are isolated."""
        manager1 = ContextManager()
        manager2 = ContextManager()
        
        manager1.add_context("Agent1", "output1")
        
        assert len(manager1.get_full_history()) == 1
        assert len(manager2.get_full_history()) == 0


class TestAddContext:
    """Test add_context method."""
    
    def test_add_context_with_valid_data(self):
        """Test adding context with valid agent name and output."""
        manager = ContextManager()
        manager.add_context("ResearcherAgent", {"findings": ["fact1", "fact2"]})
        
        history = manager.get_full_history()
        assert len(history) == 1
        assert history[0].agent_name == "ResearcherAgent"
        assert history[0].output == {"findings": ["fact1", "fact2"]}
    
    def test_add_context_with_metadata(self):
        """Test adding context with metadata."""
        manager = ContextManager()
        metadata = {"execution_time": 2.5, "status": "success"}
        manager.add_context("WriterAgent", "article content", metadata)
        
        history = manager.get_full_history()
        assert len(history) == 1
        assert history[0].metadata == metadata
    
    def test_add_context_without_metadata(self):
        """Test adding context without metadata defaults to empty dict."""
        manager = ContextManager()
        manager.add_context("EditorAgent", "edited content")
        
        history = manager.get_full_history()
        assert len(history) == 1
        assert history[0].metadata == {}
    
    def test_add_context_with_empty_agent_name_raises_error(self):
        """Test that empty agent name raises ValidationError."""
        manager = ContextManager()
        with pytest.raises(ValidationError) as exc_info:
            manager.add_context("", "output")
        assert "agent_name" in str(exc_info.value).lower()
    
    def test_add_context_multiple_times(self):
        """Test adding context multiple times appends to history."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        manager.add_context("Agent2", "output2")
        manager.add_context("Agent3", "output3")
        
        history = manager.get_full_history()
        assert len(history) == 3
        assert history[0].agent_name == "Agent1"
        assert history[1].agent_name == "Agent2"
        assert history[2].agent_name == "Agent3"
    
    def test_add_context_with_various_output_types(self):
        """Test adding context with different output types."""
        manager = ContextManager()
        
        # String output
        manager.add_context("Agent1", "string output")
        # Dict output
        manager.add_context("Agent2", {"key": "value"})
        # List output
        manager.add_context("Agent3", ["item1", "item2"])
        # Number output
        manager.add_context("Agent4", 42)
        # None output
        manager.add_context("Agent5", None)
        
        history = manager.get_full_history()
        assert len(history) == 5
        assert history[0].output == "string output"
        assert history[1].output == {"key": "value"}
        assert history[2].output == ["item1", "item2"]
        assert history[3].output == 42
        assert history[4].output is None
    
    def test_add_context_creates_timestamp(self):
        """Test that add_context automatically creates timestamp."""
        manager = ContextManager()
        manager.add_context("Agent1", "output")
        
        history = manager.get_full_history()
        timestamp = history[0].timestamp
        
        # Verify timestamp is a datetime object and is recent (within last minute)
        assert isinstance(timestamp, datetime)
        # The timestamp should be very recent (within 1 second)
        from datetime import timezone, timedelta
        now_utc = datetime.now(timezone.utc)
        time_diff = abs((now_utc - timestamp).total_seconds())
        assert time_diff < 1.0, f"Timestamp is not recent: {time_diff} seconds old"


class TestGetContext:
    """Test get_context method."""
    
    def test_get_context_for_specific_agent(self):
        """Test retrieving context for a specific agent."""
        manager = ContextManager()
        manager.add_context("ResearcherAgent", {"data": "research findings"})
        manager.add_context("WriterAgent", {"data": "article draft"})
        
        research_output = manager.get_context("ResearcherAgent")
        assert research_output == {"data": "research findings"}
        
        writer_output = manager.get_context("WriterAgent")
        assert writer_output == {"data": "article draft"}
    
    def test_get_context_for_nonexistent_agent_returns_none(self):
        """Test that getting context for nonexistent agent returns None."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        
        result = manager.get_context("NonexistentAgent")
        assert result is None
    
    def test_get_context_returns_most_recent_output(self):
        """Test that get_context returns most recent output for an agent."""
        manager = ContextManager()
        manager.add_context("Agent1", "first output")
        manager.add_context("Agent1", "second output")
        manager.add_context("Agent1", "third output")
        
        result = manager.get_context("Agent1")
        assert result == "third output"
    
    def test_get_context_without_agent_name_returns_all(self):
        """Test that get_context without agent_name returns all contexts."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        manager.add_context("Agent2", "output2")
        manager.add_context("Agent3", "output3")
        
        all_contexts = manager.get_context()
        assert isinstance(all_contexts, dict)
        assert len(all_contexts) == 3
        assert all_contexts["Agent1"] == "output1"
        assert all_contexts["Agent2"] == "output2"
        assert all_contexts["Agent3"] == "output3"
    
    def test_get_context_all_returns_most_recent_per_agent(self):
        """Test that get_context() returns most recent output per agent."""
        manager = ContextManager()
        manager.add_context("Agent1", "first")
        manager.add_context("Agent2", "output2")
        manager.add_context("Agent1", "second")
        
        all_contexts = manager.get_context()
        assert all_contexts["Agent1"] == "second"
        assert all_contexts["Agent2"] == "output2"
    
    def test_get_context_empty_manager_returns_empty_dict(self):
        """Test that get_context on empty manager returns empty dict."""
        manager = ContextManager()
        result = manager.get_context()
        assert result == {}


class TestGetFullHistory:
    """Test get_full_history method."""
    
    def test_get_full_history_returns_all_outputs(self):
        """Test that get_full_history returns all agent outputs."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        manager.add_context("Agent2", "output2")
        manager.add_context("Agent1", "output3")
        
        history = manager.get_full_history()
        assert len(history) == 3
        assert all(isinstance(item, AgentOutput) for item in history)
    
    def test_get_full_history_maintains_chronological_order(self):
        """Test that get_full_history maintains chronological order."""
        manager = ContextManager()
        manager.add_context("Agent1", "first")
        manager.add_context("Agent2", "second")
        manager.add_context("Agent3", "third")
        
        history = manager.get_full_history()
        assert history[0].output == "first"
        assert history[1].output == "second"
        assert history[2].output == "third"
    
    def test_get_full_history_returns_copy(self):
        """Test that get_full_history returns a copy, not reference."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        
        history1 = manager.get_full_history()
        history2 = manager.get_full_history()
        
        # Modifying one shouldn't affect the other
        history1.append(AgentOutput(agent_name="Agent2", output="output2"))
        
        assert len(history1) == 2
        assert len(history2) == 1
        assert len(manager.get_full_history()) == 1
    
    def test_get_full_history_empty_manager(self):
        """Test that get_full_history on empty manager returns empty list."""
        manager = ContextManager()
        history = manager.get_full_history()
        assert history == []


class TestClear:
    """Test clear method."""
    
    def test_clear_removes_all_context(self):
        """Test that clear removes all stored context."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        manager.add_context("Agent2", "output2")
        manager.add_context("Agent3", "output3")
        
        assert len(manager.get_full_history()) == 3
        
        manager.clear()
        
        assert len(manager.get_full_history()) == 0
        assert manager.get_context() == {}
    
    def test_clear_on_empty_manager(self):
        """Test that clear on empty manager doesn't raise error."""
        manager = ContextManager()
        manager.clear()  # Should not raise error
        assert len(manager.get_full_history()) == 0
    
    def test_clear_allows_new_context_after(self):
        """Test that new context can be added after clear."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        manager.clear()
        manager.add_context("Agent2", "output2")
        
        history = manager.get_full_history()
        assert len(history) == 1
        assert history[0].agent_name == "Agent2"


class TestToDict:
    """Test to_dict serialization method."""
    
    def test_to_dict_returns_dict_with_history_key(self):
        """Test that to_dict returns dict with 'history' key."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        
        result = manager.to_dict()
        assert isinstance(result, dict)
        assert 'history' in result
        assert isinstance(result['history'], list)
    
    def test_to_dict_serializes_all_outputs(self):
        """Test that to_dict serializes all agent outputs."""
        manager = ContextManager()
        manager.add_context("Agent1", "output1")
        manager.add_context("Agent2", {"key": "value"})
        
        result = manager.to_dict()
        assert len(result['history']) == 2
    
    def test_to_dict_output_is_json_serializable(self):
        """Test that to_dict output contains JSON-serializable data."""
        manager = ContextManager()
        manager.add_context("Agent1", {"data": "value"}, {"meta": "info"})
        
        result = manager.to_dict()
        
        # Check that all entries are dicts (JSON-serializable)
        for entry in result['history']:
            assert isinstance(entry, dict)
            assert 'agent_name' in entry
            assert 'output' in entry
            assert 'timestamp' in entry
            assert 'metadata' in entry
    
    def test_to_dict_empty_manager(self):
        """Test that to_dict on empty manager returns empty history."""
        manager = ContextManager()
        result = manager.to_dict()
        assert result == {'history': []}
    
    def test_to_dict_preserves_data_structure(self):
        """Test that to_dict preserves the data structure."""
        manager = ContextManager()
        test_output = {
            "findings": ["fact1", "fact2"],
            "sources": ["url1", "url2"],
            "count": 42
        }
        test_metadata = {"execution_time": 2.5}
        
        manager.add_context("ResearcherAgent", test_output, test_metadata)
        
        result = manager.to_dict()
        entry = result['history'][0]
        
        assert entry['agent_name'] == "ResearcherAgent"
        assert entry['output'] == test_output
        assert entry['metadata'] == test_metadata


class TestContextManagerIntegration:
    """Integration tests for ContextManager workflow."""
    
    def test_typical_workflow_sequence(self):
        """Test typical workflow: add contexts, retrieve, clear."""
        manager = ContextManager()
        
        # Researcher adds context
        manager.add_context("ResearcherAgent", {
            "topic": "Best Pokémon Cards",
            "sources": ["url1", "url2"],
            "findings": ["fact1", "fact2"]
        })
        
        # Writer retrieves research and adds draft
        research = manager.get_context("ResearcherAgent")
        assert research is not None
        manager.add_context("WriterAgent", {
            "draft": "Article content based on research"
        })
        
        # Editor retrieves draft and adds final
        draft = manager.get_context("WriterAgent")
        assert draft is not None
        manager.add_context("EditorAgent", {
            "final": "Edited article content"
        })
        
        # Verify all contexts are present
        all_contexts = manager.get_context()
        assert len(all_contexts) == 3
        
        # Serialize for persistence
        serialized = manager.to_dict()
        assert len(serialized['history']) == 3
        
        # Clear for next topic
        manager.clear()
        assert len(manager.get_full_history()) == 0
    
    def test_context_isolation_between_topics(self):
        """Test that context is properly isolated between topics."""
        manager = ContextManager()
        
        # Process first topic
        manager.add_context("Agent1", "topic1_output")
        assert len(manager.get_full_history()) == 1
        
        # Clear for next topic
        manager.clear()
        
        # Process second topic
        manager.add_context("Agent1", "topic2_output")
        history = manager.get_full_history()
        
        # Should only have second topic's context
        assert len(history) == 1
        assert history[0].output == "topic2_output"
