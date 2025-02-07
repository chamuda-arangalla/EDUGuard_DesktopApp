# import cv2
# import numpy as np
# from skin_analyzer import SkinAnalyzer

# class WebcamProcessor:
#     def __init__(self):
#         self.analyzer = SkinAnalyzer()
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

#             # Analyze skin
#             results = self.analyzer.calculate_dryness_score(frame)
            
#             # Display results on frame
#             self.display_results(frame, results)
            
#             # Show the frame
#             cv2.imshow('Skin Dryness Analysis', frame)
            
#             # Break loop on 'q' press
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         self.cleanup()

#     def display_results(self, frame: np.ndarray, results: dict):
#         """Display analysis results on the frame."""
#         dryness_score = results["dryness_score"]
#         texture_score = results["texture_score"]
        
#         # Add text to frame
#         cv2.putText(frame, f"Dryness Score: {dryness_score:.2f}", 
#                     (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
#         cv2.putText(frame, f"Texture Score: {texture_score:.2f}", 
#                     (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
#         # Add dryness indicator
#         if dryness_score > 0.7:
#             status = "Very Dry"
#             color = (0, 0, 255)  # Red
#         elif dryness_score > 0.4:
#             status = "Moderately Dry"
#             color = (0, 165, 255)  # Orange
#         else:
#             status = "Normal"
#             color = (0, 255, 0)  # Green
            
#         cv2.putText(frame, f"Status: {status}", 
#                     (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

#     def cleanup(self):
#         """Release resources."""
#         if self.cap is not None:
#             self.cap.release()
#         cv2.destroyAllWindows()


import cv2
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from skin_analyzer import SkinAnalyzer

class WebcamProcessor:
    def __init__(self):
        self.analyzer = SkinAnalyzer()
        self.cap = None

    def start(self):
        """Start webcam capture and analysis."""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            raise RuntimeError("Could not access webcam")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Analyze skin
            results = self.analyzer.calculate_dryness_score(frame)
            
            # Display results on frame
            self.display_results(frame, results)
            
            # Show the frame
            cv2.imshow('Skin Dryness Analysis', frame)
            
            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def display_results(self, frame: np.ndarray, results: dict):
        """Display analysis results on the frame."""
        dryness_score = results["dryness_score"]
        texture_score = results["texture_score"]
        
        # Add text to frame
        cv2.putText(frame, f"Dryness Score: {dryness_score:.2f}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"Texture Score: {texture_score:.2f}", 
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Add dryness indicator
        if dryness_score > 0.7:
            status = "Very Dry"
            color = (0, 0, 255)  # Red
        elif dryness_score > 0.4:
            status = "Moderately Dry"
            color = (0, 165, 255)  # Orange
        else:
            status = "Normal"
            color = (0, 255, 0)  # Green
            
        cv2.putText(frame, f"Status: {status}", 
                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    def evaluate_dataset_accuracy(self, dataset_path: str):
        """Evaluate the model's accuracy using a dataset."""
        # Load the dataset
        data = pd.read_csv(dataset_path)

        # Extract features and true labels
        X = data[['dryness_score', 'texture_score']].values
        y_true = data['status'].values  # True statuses from the dataset

        # Predict statuses using SkinAnalyzer
        y_pred = [self.analyzer.predict_status(row[0]) for row in X]  # Use only dryness_score for prediction

        # Calculate accuracy
        accuracy = accuracy_score(y_true, y_pred)
        print(f"Model Accuracy: {accuracy * 100:.2f}%")

    def cleanup(self):
        """Release resources."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Create an instance of the processor
    processor = WebcamProcessor()

    # Path to the dataset
    dataset_path = "./dataset/skin_analysis_data.csv"

    # Evaluate dataset accuracy
    print("Evaluating dataset accuracy...")
    processor.evaluate_dataset_accuracy(dataset_path)

    # Start webcam processing
    print("Starting webcam processing...")
    processor.start()
