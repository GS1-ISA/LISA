"""
Memory management classes for agent operations.
"""

from collections import defaultdict, deque
from datetime import datetime
from typing import Any


class AgentMemory:
    """Memory storage for agent data."""

    def __init__(self, max_size: int = 1000, retention_period: int = 3600, enable_compression: bool = True):
        self.max_size = max_size
        self.retention_period = retention_period
        self.enable_compression = enable_compression
        self._storage: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async def store(self, agent_id: str, data: dict[str, Any]) -> None:
        """Store memory data for an agent."""
        if len(self._storage[agent_id]) >= self.max_size:
            # Remove oldest entries if at max size
            self._storage[agent_id] = self._storage[agent_id][1:]

        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        self._storage[agent_id].append(data)

    async def retrieve(self, agent_id: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Retrieve memory data for an agent with optional filters."""
        memories = self._storage.get(agent_id, [])

        if filters:
            filtered_memories = []
            for memory in memories:
                if all(memory.get(key) == value for key, value in filters.items()):
                    filtered_memories.append(memory)
            return filtered_memories

        return memories.copy()

    async def cleanup(self) -> None:
        """Clean up expired memories."""
        current_time = datetime.now().timestamp()

        for agent_id in list(self._storage.keys()):
            valid_memories = []
            for memory in self._storage[agent_id]:
                if "timestamp" in memory:
                    try:
                        memory_time = datetime.fromisoformat(memory["timestamp"]).timestamp()
                        if current_time - memory_time <= self.retention_period:
                            valid_memories.append(memory)
                    except (ValueError, TypeError):
                        # Keep memories with invalid timestamps
                        valid_memories.append(memory)
                else:
                    valid_memories.append(memory)

            if valid_memories:
                self._storage[agent_id] = valid_memories
            else:
                del self._storage[agent_id]


class ConversationMemory:
    """Memory storage for conversation history."""

    def __init__(self, max_turns: int = 10, enable_context_tracking: bool = True, summarize_long_conversations: bool = True):
        self.max_turns = max_turns
        self.enable_context_tracking = enable_context_tracking
        self.summarize_long_conversations = summarize_long_conversations
        self._conversations: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_turns))

    async def add_turn(self, conversation_id: str, role: str, content: str) -> None:
        """Add a conversation turn."""
        turn = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self._conversations[conversation_id].append(turn)

    async def get_history(self, conversation_id: str) -> list[dict[str, Any]]:
        """Get conversation history."""
        return list(self._conversations[conversation_id])

    async def get_context(self, conversation_id: str) -> str:
        """Get conversation context as a string."""
        history = await self.get_history(conversation_id)
        if not history:
            return ""

        context_parts = []
        for turn in history:
            context_parts.append(f"{turn['role']}: {turn['content']}")

        return " ".join(context_parts)
