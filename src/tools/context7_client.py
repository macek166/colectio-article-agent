"""Context7 MCP client for accessing library documentation."""

import logging
from typing import Dict, Optional

from src.models.config import Config


logger = logging.getLogger(__name__)


class Context7Client:
    """Client for interacting with Context7 MCP for library documentation.

    This client provides access to up-to-date library documentation through
    the Context7 Model Context Protocol. It includes caching for frequently
    accessed documentation and graceful error handling.

    Attributes:
        config: System configuration
        cache: In-memory cache for documentation
        max_retries: Maximum number of retry attempts
    """

    def __init__(self, config: Config):
        """Initialize Context7 MCP client.

        Args:
            config: System configuration with MCP settings
        """
        self.config = config
        self.cache: Dict[str, str] = {}
        self.max_retries = config.max_retries
        logger.info("Context7Client initialized")

    def resolve_library(self, library_name: str) -> Optional[str]:
        """Resolve library name to Context7-compatible ID.

        This method attempts to resolve a library name (e.g., "crewai")
        to a Context7-compatible library ID (e.g., "/org/project").

        Args:
            library_name: Name of the library to resolve

        Returns:
            Context7-compatible library ID, or None if resolution fails
        """
        cache_key = f"resolve:{library_name}"

        # Check cache first
        if cache_key in self.cache:
            logger.debug("Returning cached library ID for: %s", library_name)
            return self.cache[cache_key]

        logger.info("Resolving library ID for: %s", library_name)

        try:
            # Import MCP tools at runtime to avoid import errors if not available
            # pylint: disable=import-outside-toplevel
            from kiro_mcp import mcp_Context7_resolve_library_id

            result = mcp_Context7_resolve_library_id(libraryName=library_name)

            if result and isinstance(result, dict):
                # Extract library ID from result
                library_id = result.get('library_id') or result.get('id')

                if library_id:
                    self.cache[cache_key] = library_id
                    logger.info(
                        "Successfully resolved library '%s' to ID: %s",
                        library_name, library_id
                    )
                    return library_id

            logger.warning("Could not resolve library ID for: %s", library_name)
            return None

        except ImportError:
            logger.warning(
                "Context7 MCP not available - continuing without library resolution"
            )
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(
                "Failed to resolve library '%s': %s - continuing without docs",
                library_name, str(e)
            )
            return None

    def get_docs(
        self,
        library_id: str,
        topic: Optional[str] = None,
        mode: str = "code"
    ) -> str:
        """Fetch documentation for a library.

        This method retrieves documentation from Context7 MCP for the specified
        library. It supports both 'code' mode (API references, code examples)
        and 'info' mode (conceptual guides, architecture).

        Args:
            library_id: Context7-compatible library ID (e.g., "/org/project")
            topic: Optional specific topic to focus on
            mode: Documentation mode - 'code' for API refs, 'info' for guides

        Returns:
            Documentation content as string, or empty string if fetch fails
        """
        if mode not in ("code", "info"):
            logger.warning("Invalid mode '%s', defaulting to 'code'", mode)
            mode = "code"

        # Create cache key
        cache_key = f"docs:{library_id}:{topic or 'general'}:{mode}"

        # Check cache first
        if cache_key in self.cache:
            logger.debug("Returning cached documentation for: %s", library_id)
            return self.cache[cache_key]

        logger.info(
            "Fetching documentation for library: %s (topic: %s, mode: %s)",
            library_id, topic or "general", mode
        )

        try:
            # Import MCP tools at runtime
            # pylint: disable=import-outside-toplevel
            from kiro_mcp import mcp_Context7_get_library_docs

            result = mcp_Context7_get_library_docs(
                context7CompatibleLibraryID=library_id,
                topic=topic,
                mode=mode
            )

            if result:
                # Extract documentation content
                if isinstance(result, str):
                    docs = result
                elif isinstance(result, dict):
                    docs = result.get('content') or result.get('documentation') or str(result)
                else:
                    docs = str(result)

                # Cache the result
                self.cache[cache_key] = docs
                logger.info(
                    "Successfully fetched documentation for: %s (%d chars)",
                    library_id, len(docs)
                )
                return docs

            logger.warning("No documentation returned for: %s", library_id)
            return ""

        except ImportError:
            logger.warning(
                "Context7 MCP not available - continuing without documentation"
            )
            return ""
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(
                "Failed to fetch documentation for '%s': %s - continuing without docs",
                library_id, str(e)
            )
            return ""

    def clear_cache(self) -> None:
        """Clear the documentation cache.

        This method removes all cached documentation entries. Useful for
        forcing fresh documentation retrieval or managing memory usage.
        """
        cache_size = len(self.cache)
        self.cache.clear()
        logger.info("Cleared documentation cache (%d entries)", cache_size)

    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the documentation cache.

        Returns:
            Dictionary with cache statistics (size, entries)
        """
        return {
            'entries': len(self.cache),
            'total_size': sum(len(v) for v in self.cache.values())
        }
