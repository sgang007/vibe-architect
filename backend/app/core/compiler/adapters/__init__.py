from .base import AbstractPlatformAdapter, PromptSection
from .replit import ReplitAdapter
from .bolt import BoltAdapter
from .lovable import LovableAdapter
from .v0 import V0Adapter
from .cursor import CursorAdapter
from .emergent import EmergentAdapter

PLATFORM_ADAPTERS = {
    "replit": ReplitAdapter,
    "bolt": BoltAdapter,
    "lovable": LovableAdapter,
    "v0": V0Adapter,
    "cursor": CursorAdapter,
    "emergent": EmergentAdapter,
}


def get_platform_adapter(platform: str) -> AbstractPlatformAdapter:
    cls = PLATFORM_ADAPTERS.get(platform.lower())
    if not cls:
        raise ValueError(f"Unknown platform: {platform}. Choose from: {list(PLATFORM_ADAPTERS.keys())}")
    return cls()
