"""Context Manager for managing agent outputs and conversation history.

This module provides the ContextManager class which handles storage and retrieval
of agent outputs throughout the content generation workflow. It uses Pydantic
models for validation and provides context isolation between ContentCrew instances.
"""

from typing import Any, Dict, List, Optional

from src.models.agent_output import AgentOutput


class ContextManager:
    """Manages context and conversation history for agent interactions.

    The ContextManager stores agent outputs using Pydantic validation and provides
    methods to add, retrieve, and clear context. It maintains isolation between
    different ContentCrew instances by clearing context after each topic completion.

    Attributes:
        _context: Internal storage for agent outputs as AgentOutput instances
    """

    def __init__(self) -> None:
        """Initialize empty context storage."""
        self._context: List[AgentOutput] = []

    def add_context(
        self,
        agent_name: str,
        output: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store output from an agent with Pydantic validation.

        Creates an AgentOutput instance with the provided data and appends it
        to the context history. The AgentOutput model automatically validates
        the agent_name and adds a timestamp.

        Args:
            agent_name: Name of the agent producing the output (must be non-empty)
            output: The actual output data from the agent (can be any type)
            metadata: Optional additional metadata about the output

        Raises:
            ValidationError: If agent_name is empty or invalid

        Example:
            >>> manager = ContextManager()
            >>> manager.add_context(
            ...     "ResearcherAgent",
            ...     {"findings": ["fact1", "fact2"]},
            ...     {"execution_time": 2.5}
            ... )
        """
        if metadata is None:
            metadata = {}

        # Create AgentOutput with Pydantic validation
        agent_output = AgentOutput(
            agent_name=agent_name,
            output=output,
            metadata=metadata
        )

        self._context.append(agent_output)

    def get_context(self, agent_name: Optional[str] = None) -> Any:
        """Retrieve context from specific agent or all agents.

        If agent_name is provided, returns the output from the most recent
        execution of that agent. If agent_name is None, returns a dictionary
        mapping agent names to their most recent outputs.

        Args:
            agent_name: Optional name of specific agent to retrieve context from.
                       If None, returns all agent contexts.

        Returns:
            If agent_name is specified: The output from that agent's most recent
                execution, or None if the agent hasn't produced output yet.
            If agent_name is None: Dictionary mapping agent names to their most
                recent outputs.

        Example:
            >>> manager = ContextManager()
            >>> manager.add_context("ResearcherAgent", {"data": "value"})
            >>> manager.get_context("ResearcherAgent")
            {'data': 'value'}
            >>> manager.get_context()
            {'ResearcherAgent': {'data': 'value'}}
        """
        if agent_name is not None:
            # Find the most recent output from the specified agent
            for agent_output in reversed(self._context):
                if agent_output.agent_name == agent_name:
                    return agent_output.output
            return None

        # Return all agent contexts as a dictionary
        result: Dict[str, Any] = {}
        for agent_output in self._context:
            # Keep only the most recent output for each agent
            result[agent_output.agent_name] = agent_output.output

        return result

    def get_full_history(self) -> List[AgentOutput]:
        """Get complete conversation history with all agent outputs.

        Returns the full list of AgentOutput instances in chronological order,
        including all executions from all agents. This is useful for debugging,
        logging, or persisting the complete context to a database.

        Returns:
            List of AgentOutput instances in chronological order

        Example:
            >>> manager = ContextManager()
            >>> manager.add_context("Agent1", "output1")
            >>> manager.add_context("Agent2", "output2")
            >>> history = manager.get_full_history()
            >>> len(history)
            2
            >>> history[0].agent_name
            'Agent1'
        """
        return self._context.copy()

    def clear(self) -> None:
        """Clear all context (used between ContentCrew instances).

        Removes all stored agent outputs to provide context isolation between
        different topic processing sessions. This should be called after each
        ContentCrew completes processing a topic.

        Example:
            >>> manager = ContextManager()
            >>> manager.add_context("Agent1", "output1")
            >>> len(manager.get_full_history())
            1
            >>> manager.clear()
            >>> len(manager.get_full_history())
            0
        """
        self._context.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context for persistence.

        Converts the context history to a dictionary format suitable for
        JSON serialization or database storage. Each AgentOutput is converted
        to its dictionary representation using Pydantic's model_dump method.

        Returns:
            Dictionary containing the serialized context with a 'history' key
            containing the list of agent outputs

        Example:
            >>> manager = ContextManager()
            >>> manager.add_context("Agent1", {"key": "value"})
            >>> data = manager.to_dict()
            >>> 'history' in data
            True
            >>> len(data['history'])
            1
        """
        return {
            'history': [
                agent_output.model_dump(mode='json')
                for agent_output in self._context
            ]
        }
