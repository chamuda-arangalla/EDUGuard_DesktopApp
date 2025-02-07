# import cv2
# import numpy as np
# from typing import Tuple, Dict

# class SkinAnalyzer:
#     def __init__(self):
#         self.dry_skin_threshold = 0.6
#         self.texture_threshold = 30

#     def detect_skin(self, frame: np.ndarray) -> np.ndarray:
#         """Convert the frame to YCrCb color space and detect skin pixels."""
#         ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
#         skin_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
#         return skin_mask

#     def analyze_texture(self, frame: np.ndarray, skin_mask: np.ndarray) -> float:
#         """Analyze skin texture using Laplacian operator."""
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         skin_gray = cv2.bitwise_and(gray, gray, mask=skin_mask)
#         laplacian = cv2.Laplacian(skin_gray, cv2.CV_64F)
#         texture_score = np.mean(np.abs(laplacian))
#         return texture_score

#     def calculate_dryness_score(self, frame: np.ndarray) -> Dict[str, float]:
#         """Calculate skin dryness score based on color and texture analysis."""
#         skin_mask = self.detect_skin(frame)
#         texture_score = self.analyze_texture(frame, skin_mask)
        
#         # Normalize texture score
#         normalized_texture = min(1.0, texture_score / self.texture_threshold)
        
#         # Calculate dryness score (higher score means more dryness)
#         dryness_score = normalized_texture
        
#         return {
#             "dryness_score": dryness_score,
#             "texture_score": texture_score
#         }



import cv2
import numpy as np
from typing import Tuple, Dict


class SkinAnalyzer:
    def __init__(self):
        self.dry_skin_threshold = 0.7 
        self.moderately_dry_threshold = 0.4 
        self.texture_threshold = 30 

    def detect_skin(self, frame: np.ndarray) -> np.ndarray:
        # """Convert the frame to YCrCb color space and detect skin pixels."""
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        skin_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
        return skin_mask

    def analyze_texture(self, frame: np.ndarray, skin_mask: np.ndarray) -> float:
        # """Analyze skin texture using Laplacian operator."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        skin_gray = cv2.bitwise_and(gray, gray, mask=skin_mask)
        laplacian = cv2.Laplacian(skin_gray, cv2.CV_64F)
        texture_score = np.mean(np.abs(laplacian))
        return texture_score

    def calculate_dryness_score(self, frame: np.ndarray) -> Dict[str, float]:
        # """Calculate skin dryness score based on color and texture analysis."""
        skin_mask = self.detect_skin(frame)
        texture_score = self.analyze_texture(frame, skin_mask)
        
        # Normalize texture score
        normalized_texture = min(1.0, texture_score / self.texture_threshold)
        
        # Calculate dryness score (higher score means more dryness)
        dryness_score = normalized_texture
        
        return {
            "dryness_score": dryness_score,
            "texture_score": texture_score
        }

    def predict_status(self, dryness_score: float) -> str:
        """
        Predict skin status based on dryness score.
        - dryness_score > 0.7: Very Dry
        - 0.4 < dryness_score <= 0.7: Moderately Dry
        - dryness_score <= 0.4: Normal
        """
        if dryness_score > self.dry_skin_threshold:
            return "Very Dry"
        elif dryness_score > self.moderately_dry_threshold:
            return "Moderately Dry"
        else:
            return "Normal"
