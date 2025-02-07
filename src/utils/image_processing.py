"""
Image processing utilities for skin analysis.
"""
import cv2
import numpy as np

def normalize_score(score: float, threshold: float) -> float:
    """Normalize a score between 0 and 1."""
    return min(1.0, score / threshold)

def draw_text(frame: np.ndarray, text: str, position: tuple, 
              color: tuple = (0, 0, 255), scale: float = 1) -> None:
    """Draw text on frame with consistent styling."""
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                scale, color, 2)