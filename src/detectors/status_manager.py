"""
Manages hydration status and override functionality.
"""
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class HydrationStatus:
    is_override: bool = False
    override_end_time: Optional[float] = None
    status: str = "Normal"

class HydrationManager:
    def __init__(self, override_duration: int = 15 * 60):
        self.override_duration = override_duration
        self.status = HydrationStatus()

    def set_drinking_override(self) -> None:
        """Set hydration status override after drinking detection."""
        self.status.is_override = True
        self.status.override_end_time = time.time() + self.override_duration
        self.status.status = "Normal"

    def get_current_status(self) -> HydrationStatus:
        """Get current hydration status, clearing override if expired."""
        if (self.status.is_override and 
            self.status.override_end_time and 
            time.time() >= self.status.override_end_time):
            self._clear_override()
        return self.status

    def _clear_override(self) -> None:
        """Clear the override status."""
        self.status.is_override = False
        self.status.override_end_time = None