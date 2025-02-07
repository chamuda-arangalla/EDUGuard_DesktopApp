"""
Visualization utilities for skin analysis results.
"""
import cv2
import numpy as np
from typing import Dict

def draw_analysis_overlay(frame: np.ndarray, results: Dict[str, float]) -> None:
    """Draw analysis results overlay on the frame."""
    dryness_score = results["dryness_score"]
    texture_score = results["texture_score"]
    
    # Draw background rectangle for better text visibility
    overlay = frame.copy()
    cv2.rectangle(overlay, (5, 5), (300, 120), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    
    # Draw scores and status
    draw_text(frame, f"Dryness Score: {dryness_score:.2f}", (10, 30))
    draw_text(frame, f"Texture Score: {texture_score:.2f}", (10, 70))
    
    status, color = get_status_info(dryness_score)
    draw_text(frame, f"Status: {status}", (10, 110), color)

def draw_text(frame: np.ndarray, text: str, position: tuple, 
              color: tuple = (255, 255, 255), scale: float = 0.7) -> None:
    """Draw text with a black outline for better visibility."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 2
    
    # Draw black outline
    cv2.putText(frame, text, position, font, scale, (0, 0, 0), thickness + 1)
    # Draw text in specified color
    cv2.putText(frame, text, position, font, scale, color, thickness)

def get_status_info(dryness_score: float) -> tuple:
    """Get status text and color based on dryness score."""
    if dryness_score > 0.7:
        return "Very Dry", (0, 0, 255)  # Red
    elif dryness_score > 0.4:
        return "Moderately Dry", (0, 165, 255)  # Orange
    return "Normal", (0, 255, 0)  # Green