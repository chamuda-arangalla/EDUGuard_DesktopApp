# """
# Webcam capture and processing functionality.
# """
import cv2
import numpy as np
from ..analyzers.skin_analyzer import SkinAnalyzer
from ..utils.visualization import draw_analysis_overlay
from ..data.dataset_manager import DatasetManager

class WebcamProcessor:
    def __init__(self):
        self.analyzer = SkinAnalyzer()
        self.dataset_manager = DatasetManager()
        self.cap = None

    def start(self):
        # """Start webcam capture and analysis."""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            raise RuntimeError("Could not access webcam")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Analyze skin and save results
            results = self.analyzer.calculate_dryness_score(frame)
            self.dataset_manager.save_analysis(results)
            
            # Display results
            draw_analysis_overlay(frame, results)
            cv2.imshow('Skin Dryness Analysis', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def cleanup(self):
        """Release resources."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()






# """
# Webcam capture and processing functionality with drinking water action detection.
# """
# import cv2
# import time
# import mediapipe as mp
# import numpy as np
# from ..analyzers.skin_analyzer import SkinAnalyzer
# from ..utils.visualization import draw_analysis_overlay
# from ..data.dataset_manager import DatasetManager


# class WebcamProcessor:
#     def __init__(self):
#         self.analyzer = SkinAnalyzer()
#         self.dataset_manager = DatasetManager()
#         self.cap = None
#         self.override_status = None
#         self.override_end_time = None

#         # Initialize MediaPipe Pose
#         self.mp_pose = mp.solutions.pose
#         self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#         self.mp_drawing = mp.solutions.drawing_utils  # For drawing pose landmarks

#     def start(self):
#         """Start webcam capture and analysis."""
#         self.cap = cv2.VideoCapture(0)

#         if not self.cap.isOpened():
#             raise RuntimeError("Could not access webcam")

#         while True:
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             # Convert frame to RGB for MediaPipe processing
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = self.pose.process(rgb_frame)

#             # Draw pose landmarks for debugging
#             self.draw_pose_landmarks(frame, results)

#             # Detect drinking water action
#             if self.is_drinking_water(results):
#                 self.override_status = "Normal"
#                 self.override_end_time = time.time() + 15 * 60  # Set override for 15 minutes

#                 # Display "Drinking Water" on the screen
#                 self.display_drinking_message(frame)

#             # Check override status
#             if self.override_status and time.time() < self.override_end_time:
#                 # Display override status
#                 results_data = {"dryness_score": 0.0, "texture_score": 0.0, "status": self.override_status}
#             else:
#                 # Perform normal skin analysis
#                 results_data = self.analyzer.calculate_dryness_score(frame)
#                 if self.override_status and time.time() >= self.override_end_time:
#                     # Clear override if time has passed
#                     self.override_status = None
#                     self.override_end_time = None

#             # Save results
#             self.dataset_manager.save_analysis(results_data)

#             # Display results
#             draw_analysis_overlay(frame, results_data)
#             cv2.imshow('Skin Dryness Analysis', frame)

#             # Break loop on 'q' press
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         self.cleanup()

#     def is_drinking_water(self, results) -> bool:
#         """
#         Detect if a user is drinking water using pose estimation.
#         """
#         if not results.pose_landmarks:
#             return False

#         # Get key landmarks
#         landmarks = results.pose_landmarks.landmark
#         mouth = landmarks[self.mp_pose.PoseLandmark.MOUTH_LEFT]
#         left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
#         right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]

#         # Calculate distances between wrists and mouth
#         left_distance = np.sqrt(
#             (mouth.x - left_wrist.x) ** 2 +
#             (mouth.y - left_wrist.y) ** 2 +
#             (mouth.z - left_wrist.z) ** 2
#         )
#         right_distance = np.sqrt(
#             (mouth.x - right_wrist.x) ** 2 +
#             (mouth.y - right_wrist.y) ** 2 +
#             (mouth.z - right_wrist.z) ** 2
#         )

#         # Debugging: Print distances for tuning threshold
#         print(f"Left Distance: {left_distance:.2f}, Right Distance: {right_distance:.2f}")

#         # Heuristic: If either wrist is close to the mouth, assume drinking action
#         return left_distance < 0.1 or right_distance < 0.1  # Adjust threshold based on testing

#     def draw_pose_landmarks(self, frame, results):
#         """Draw pose landmarks on the frame for debugging."""
#         if results.pose_landmarks:
#             self.mp_drawing.draw_landmarks(
#                 frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
#             )

#     def display_drinking_message(self, frame):
#         """Display 'Drinking Water' message on the screen."""
#         message = "Drinking Water"
#         cv2.putText(frame, message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#     def cleanup(self):
#         """Release resources."""
#         if self.cap is not None:
#             self.cap.release()
#         cv2.destroyAllWindows()


# if __name__ == "__main__":
#     processor = WebcamProcessor()
#     processor.start()







# """
# Webcam capture and processing functionality with drinking water detection.
# """
# import cv2
# import time
# import numpy as np
# from ..analyzers.skin_analyzer import SkinAnalyzer
# from ..utils.visualization import draw_analysis_overlay
# from ..data.dataset_manager import DatasetManager


# class WebcamProcessor:
#     def __init__(self):
#         self.analyzer = SkinAnalyzer()
#         self.dataset_manager = DatasetManager()
#         self.cap = None
#         self.override_status = None
#         self.override_end_time = None

#         # HSV thresholds for detecting water (adjust based on your use case)
#         self.water_lower = np.array([100, 150, 0], dtype='uint8')  # Example: blue water
#         self.water_upper = np.array([140, 255, 255], dtype='uint8')
#         self.drink_cooldown = 15 * 60  # 15 minutes cooldown
#         self.last_drink_time = 0

#     def start(self):
#         """Start webcam capture and analysis."""
#         self.cap = cv2.VideoCapture(0)

#         if not self.cap.isOpened():
#             raise RuntimeError("Could not access webcam")

#         while True:
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             # Detect drinking water action and apply cooldown
#             if self.detect_drinking(frame):
#                 self.last_drink_time = time.time()  # Update last drink time
#                 self.override_status = "Normal"
#                 self.override_end_time = time.time() + self.drink_cooldown
#                 self.display_drinking_message(frame)

#             # Check override status
#             if self.override_status and time.time() < self.override_end_time:
#                 results_data = {"dryness_score": 0.0, "texture_score": 0.0, "status": self.override_status}
#             else:
#                 # Perform normal skin analysis
#                 results_data = self.analyzer.calculate_dryness_score(frame)
#                 if self.override_status and time.time() >= self.override_end_time:
#                     # Clear override if cooldown is over
#                     self.override_status = None
#                     self.override_end_time = None

#             # Save results
#             self.dataset_manager.save_analysis(results_data)

#             # Display results
#             draw_analysis_overlay(frame, results_data)
#             cv2.imshow('Skin Dryness Analysis', frame)

#             # Break loop on 'q' press
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         self.cleanup()

#     def detect_drinking(self, frame):
#         """
#         Detect if a user is drinking water using HSV thresholds.
#         """
#         hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#         water_mask = cv2.inRange(hsv, self.water_lower, self.water_upper)
#         contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         # Check if any detected contour corresponds to a significant water bottle area
#         for contour in contours:
#             if cv2.contourArea(contour) > 1000:  # Minimum area threshold for water detection
#                 return True
#         return False

#     def display_drinking_message(self, frame):
#         """Display 'Drinking Water' message on the screen."""
#         message = "Drinking Water"
#         cv2.putText(frame, message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#     def cleanup(self):
#         """Release resources."""
#         if self.cap is not None:
#             self.cap.release()
#         cv2.destroyAllWindows()


# if __name__ == "__main__":
#     processor = WebcamProcessor()
#     processor.start()





# """
# Webcam capture and processing functionality with drinking water detection.
# """
# import cv2
# from ..analyzers.skin_analyzer import SkinAnalyzer
# from ..utils.visualization import draw_analysis_overlay
# from ..data.dataset_manager import DatasetManager
# from ..detectors.water_detector import WaterDetector
# from ..detectors.status_manager import HydrationManager

# class WebcamProcessor:
#     def __init__(self):
#         self.analyzer = SkinAnalyzer()
#         self.dataset_manager = DatasetManager()
#         self.water_detector = WaterDetector()
#         self.hydration_manager = HydrationManager()
#         self.cap = None

#     def start(self):
#         """Start webcam capture and analysis."""
#         self.cap = cv2.VideoCapture(0)
        
#         if not self.cap.isOpened():
#             raise RuntimeError("Could not access webcam")

#         while True:
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             # Detect drinking water
#             is_drinking, frame = self.water_detector.detect(frame)
#             if is_drinking:
#                 self.hydration_manager.set_drinking_override()

#             # Get current hydration status
#             hydration_status = self.hydration_manager.get_current_status()

#             # Process frame based on hydration status
#             if hydration_status.is_override:
#                 results = {
#                     "dryness_score": 0.0,
#                     "texture_score": 0.0,
#                     "status": hydration_status.status
#                 }
#             else:
#                 results = self.analyzer.calculate_dryness_score(frame)

#             # Save and display results
#             self.dataset_manager.save_analysis(results)
#             draw_analysis_overlay(frame, results)
#             cv2.imshow('Skin Dryness Analysis', frame)

#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         self.cleanup()

#     def cleanup(self):
#         """Release resources."""
#         if self.cap is not None:
#             self.cap.release()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     processor = WebcamProcessor()
#     processor.start()







# """
# Webcam capture and processing functionality with liveness detection and resized display window.
# """
# import cv2
# import numpy as np
# from ..analyzers.skin_analyzer import SkinAnalyzer
# from ..utils.visualization import draw_analysis_overlay
# from ..data.dataset_manager import DatasetManager

# class WebcamProcessor:
#     def __init__(self):
#         self.analyzer = SkinAnalyzer()
#         self.dataset_manager = DatasetManager()
#         self.cap = None
#         self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # Haar cascade for face detection

#     def start(self):
#         """Start webcam capture and analysis."""
#         self.cap = cv2.VideoCapture(0)

#         if not self.cap.isOpened():
#             raise RuntimeError("Could not access webcam")

#         # Get screen resolution
#         screen_width = 1920  # Replace with your screen width
#         screen_height = 1180  # Replace with your screen height

#         # Calculate half-screen size
#         half_width = screen_width // 2
#         half_height = screen_height // 2

#         # Create named window and resize it
#         cv2.namedWindow('Skin Dryness Analysis', cv2.WINDOW_NORMAL)
#         cv2.resizeWindow('Skin Dryness Analysis', half_width, half_height)

#         while True:
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             # Detect face for liveness
#             if not self.is_user_present(frame):
#                 # No user detected, set display to null
#                 frame = self.display_null_results(frame)
#             else:
#                 # Analyze skin and save results
#                 results = self.analyzer.calculate_dryness_score(frame)
#                 self.dataset_manager.save_analysis(results)

#                 # Display results
#                 draw_analysis_overlay(frame, results)

#             # Show the frame
#             cv2.imshow('Skin Dryness Analysis', frame)

#             # Break loop on 'q' press
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         self.cleanup()

#     def is_user_present(self, frame: np.ndarray) -> bool:
#         """Detect if a user is present in the frame using face detection."""
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale for face detection
#         faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
#         return len(faces) > 0  # Return True if at least one face is detected

#     def display_null_results(self, frame: np.ndarray) -> np.ndarray:
#         """Display null results when no user is detected."""
#         cv2.putText(frame, "No user detected. Please position yourself in front of the camera.", 
#                     (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#         return frame

#     def cleanup(self):
#         """Release resources."""
#         if self.cap is not None:
#             self.cap.release()
#         cv2.destroyAllWindows()






# """
# Webcam capture and processing functionality with notification support and proper cleanup.
# """
# import cv2
# import numpy as np
# import signal
# import sys
# from plyer import notification  # For sending notifications
# from ..analyzers.skin_analyzer import SkinAnalyzer
# from ..utils.visualization import draw_analysis_overlay
# from ..data.dataset_manager import DatasetManager


# class WebcamProcessor:
#     def __init__(self):
#         self.analyzer = SkinAnalyzer()
#         self.dataset_manager = DatasetManager()
#         self.cap = None
#         self.notifications_enabled = True  # Flag to control notifications

#     def start(self):
#         """Start webcam capture and analysis."""
#         self.cap = cv2.VideoCapture(0)
        
#         if not self.cap.isOpened():
#             raise RuntimeError("Could not access webcam")

#         while True:
#             ret, frame = self.cap.read()
#             if not ret:
#                 break

#             # Analyze skin and save results
#             results = self.analyzer.calculate_dryness_score(frame)
#             self.dataset_manager.save_analysis(results)
            
#             # Send notification based on dryness status
#             self.send_notification(results["dryness_score"])
            
#             # Display results
#             draw_analysis_overlay(frame, results)
#             cv2.imshow('Skin Dryness Analysis', frame)
            
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         self.cleanup()

#     def send_notification(self, dryness_score):
#         """Send notification based on dryness score."""
#         if not self.notifications_enabled:
#             return  # Do not send notifications if the flag is disabled

#         if dryness_score > 0.7:
#             notification.notify(
#                 title="Skin Alert: Severe Dryness",
#                 message="You're dehydrated. Drink water now!",
#                 app_name="Skin Analyzer",
#                 timeout=5  # Notification duration in seconds
#             )
#         elif dryness_score > 0.4:
#             notification.notify(
#                 title="Skin Alert: Moderate Dryness",
#                 message="You're about to get dehydrated. Drink water soon!",
#                 app_name="Skin Analyzer",
#                 timeout=5
#             )

#     def cleanup(self):
#         """Release resources and stop notifications."""
#         if self.cap is not None:
#             self.cap.release()
#         cv2.destroyAllWindows()
#         self.notifications_enabled = False  # Disable notifications
#         print("Cleanup completed. Notifications stopped.")


# def signal_handler(sig, frame):
#     """Handle application exit."""
#     print("Exiting application...")
#     processor.cleanup()
#     sys.exit(0)


# if __name__ == "__main__":
#     # Create processor instance
#     processor = WebcamProcessor()

#     # Register signal handler for graceful exit
#     signal.signal(signal.SIGINT, signal_handler)

#     # Start processing
#     processor.start()

