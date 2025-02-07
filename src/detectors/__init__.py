"""
Initialize detectors module.
"""
from .water_detector import WaterDetector
from .status_manager import HydrationManager

__all__ = ['WaterDetector', 'HydrationManager']