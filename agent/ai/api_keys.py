"""
Gemini API Key Manager with Round-Robin Rotation

Provides thread-safe rotation through multiple API keys to avoid rate limits.
"""

import threading
from typing import List


class APIKeyManager:
    """Thread-safe round-robin API key manager."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._keys: List[str] = []
        self._index = 0
        self._key_lock = threading.Lock()

    def set_keys(self, keys: List[str]):
        """Set the list of API keys."""
        with self._key_lock:
            self._keys = [k.strip() for k in keys if k.strip()]
            self._index = 0
            print(f"[APIKeyManager] Loaded {len(self._keys)} API keys")

    def get_next_key(self) -> str:
        """Get the next API key in round-robin order."""
        with self._key_lock:
            if not self._keys:
                raise ValueError("No API keys configured")

            key = self._keys[self._index]
            self._index = (self._index + 1) % len(self._keys)
            return key

    def get_key_for_agent(self, agent_id: int) -> str:
        """Get a specific key for an agent (for parallel execution)."""
        with self._key_lock:
            if not self._keys:
                raise ValueError("No API keys configured")

            # Assign keys based on agent ID to avoid collisions
            idx = agent_id % len(self._keys)
            return self._keys[idx]

    @property
    def key_count(self) -> int:
        return len(self._keys)


# Global instance
_manager = None


def get_key_manager() -> APIKeyManager:
    """Get the global API key manager instance."""
    global _manager
    if _manager is None:
        _manager = APIKeyManager()
    return _manager


def setup_keys(keys: List[str]):
    """Initialize the API key manager with keys."""
    manager = get_key_manager()
    manager.set_keys(keys)


def get_next_key() -> str:
    """Get the next API key."""
    return get_key_manager().get_next_key()


# API Keys should be loaded from environment variables or secure config file
# Add your keys to .env file: GEMINI_API_KEYS=key1,key2,key3
GEMINI_API_KEYS = []

# Model configuration
GEMINI_MODEL = "gemini-2.5-pro"


def init_default_keys():
    """Initialize with default keys."""
    setup_keys(GEMINI_API_KEYS)


# Auto-initialize on import
init_default_keys()
