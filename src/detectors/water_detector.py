"""
Water drinking detection functionality using HSV color thresholding.
"""
import cv2
import numpy as np
import time
from typing import Tuple

class WaterDetector:
    def __init__(self):
        # HSV thresholds for detecting water (blue-ish color)
        self.water_lower = np.array([100, 150, 0], dtype='uint8')
        self.water_upper = np.array([140, 255, 255], dtype='uint8')
        self.min_area = 1000  # Minimum contour area to detect water
        self.cooldown_period = 15 * 60  # 15 minutes cooldown
        self.last_detection_time = 0

    def detect(self, frame: np.ndarray) -> Tuple[bool, np.ndarray]:
        """
        Detect water drinking action in the frame.
        Returns: Tuple of (is_drinking, processed_frame)
        """
        current_time = time.time()
        if current_time - self.last_detection_time < self.cooldown_period:
            return False, frame

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        water_mask = cv2.inRange(hsv, self.water_lower, self.water_upper)
        contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        is_drinking = any(cv2.contourArea(contour) > self.min_area for contour in contours)
        
        if is_drinking:
            self.last_detection_time = current_time
            self._draw_detection_message(frame)

        return is_drinking, frame

    def _draw_detection_message(self, frame: np.ndarray) -> None:
        """Draw drinking detection message on the frame."""
        cv2.putText(frame, "Drinking Water Detected", 
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0), 2)