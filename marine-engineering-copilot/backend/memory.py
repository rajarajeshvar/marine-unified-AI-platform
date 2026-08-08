"""
Marine Guardian AI — Conversational Memory

Manages per-session conversation history for multi-turn context.
Includes context-aware query expansion for follow-up questions.
"""

import re
from collections import defaultdict
from config import MAX_CONVERSATION_TURNS


# Patterns that indicate a follow-up referencing previous context
_PRONOUN_PATTERNS = re.compile(
    r'\b(that|it|this|those|these|the reading|the value|the level|the engine)\b',
    re.IGNORECASE
)

_SHORT_FOLLOWUP_PATTERNS = re.compile(
    r'^(is\s+(that|it|this)|why|what\s+should|what\s+do|how\s+(do|should|can)|should\s+i|'
    r'can\s+you|tell\s+me\s+more|what\s+about|and\s+the|show\s+me|what\s+caused|'
    r'what\s+else|anything\s+else|is\s+there|how\s+bad)',
    re.IGNORECASE
)


class ConversationMemory:
    """In-memory session-based conversation store with context-aware query expansion."""

    def __init__(self):
        self._sessions: dict[str, list[dict]] = defaultdict(list)

    def add_turn(self, session_id: str, role: str, content: str):
        """Add a conversation turn to the session."""
        self._sessions[session_id].append({"role": role, "content": content})
        # Trim to max turns
        if len(self._sessions[session_id]) > MAX_CONVERSATION_TURNS * 2:
            self._sessions[session_id] = self._sessions[session_id][-(MAX_CONVERSATION_TURNS * 2):]

    def get_history(self, session_id: str) -> str:
        """Format conversation history for the LLM prompt."""
        turns = self._sessions.get(session_id, [])
        if not turns:
            return "No previous conversation."

        formatted = []
        for turn in turns:
            prefix = "Engineer" if turn["role"] == "user" else "Copilot"
            formatted.append(f"{prefix}: {turn['content']}")

        return "\n".join(formatted)

    def get_contextual_query(self, session_id: str, current_message: str) -> str:
        """
        Produce a retrieval query that includes necessary context from conversation
        history — but ONLY when the current message actually needs it.

        Constraint #1: Standalone questions are preserved exactly.
        Only short follow-ups with pronouns/implicit references get expanded.
        """
        turns = self._sessions.get(session_id, [])
        if not turns:
            # No history — the message is standalone by definition
            return current_message

        msg_lower = current_message.lower().strip()
        msg_word_count = len(msg_lower.split())

        # Heuristic: A message is likely a standalone question if it is long enough
        # and contains its own subject/topic (not just pronouns).
        # Only expand short messages (< 10 words) that contain pronoun references
        # or match known follow-up patterns.
        needs_expansion = False

        if msg_word_count < 10:
            # Check for pronoun references
            if _PRONOUN_PATTERNS.search(msg_lower):
                needs_expansion = True
            # Check for short follow-up patterns
            elif _SHORT_FOLLOWUP_PATTERNS.search(msg_lower):
                needs_expansion = True
            # Very short queries (1-4 words) like "why?" or "what next?"
            elif msg_word_count <= 4:
                needs_expansion = True

        if not needs_expansion:
            return current_message

        # Find the most recent topic from conversation history
        topic_context = self._extract_recent_topic(turns)
        if not topic_context:
            return current_message

        # Build an expanded query that combines the topic with the follow-up
        expanded = f"{current_message} (context: {topic_context})"
        return expanded

    def _extract_recent_topic(self, turns: list[dict]) -> str:
        """
        Extract the most recent topical context from conversation turns.
        Returns a short summary string of the topic being discussed.
        """
        # Look at the last few user messages to find the topic
        recent_user_messages = []
        for turn in reversed(turns):
            if turn["role"] == "user":
                recent_user_messages.append(turn["content"])
                if len(recent_user_messages) >= 2:
                    break

        if not recent_user_messages:
            return ""

        # The most recent user message is the primary topic reference
        # Take the most recent substantive user message (longest one, or the first)
        topic_msg = recent_user_messages[0]

        # If the most recent message is itself very short, look at the one before
        if len(topic_msg.split()) < 5 and len(recent_user_messages) > 1:
            topic_msg = recent_user_messages[1]

        # Also look at the most recent assistant response for key values
        for turn in reversed(turns):
            if turn["role"] == "assistant":
                # Extract key numbers and equipment mentions from the response
                assistant_snippet = turn["content"][:200]
                # If the assistant mentioned specific readings, include them
                return f"{topic_msg}. Previous answer context: {assistant_snippet}"

        return topic_msg

    def clear_session(self, session_id: str):
        """Clear a session's conversation history."""
        self._sessions.pop(session_id, None)


# Global singleton
memory = ConversationMemory()
