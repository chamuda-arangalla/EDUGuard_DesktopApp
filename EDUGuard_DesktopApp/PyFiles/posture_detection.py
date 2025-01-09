import cv2
import mediapipe as mp
import numpy as np
import joblib
import json
import time
from collections import deque
from pymongo import MongoClient
import sys

# MongoDB connection setup
MONGO_URI = "mongodb+srv://myUser:myPassword123@cluster0.qk0epky.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["EDUGuardDB"]  # Replace with your database name
users_collection = db["Users"]  # Replace with your collection name

# Get the authenticated user email from command-line arguments
if len(sys.argv) < 2:
    print("Error: No email provided as an argument.")
    sys.exit(1)

USER_EMAIL = sys.argv[1]  # Get the user email from the arguments

# Load the .pkl model
model = joblib.load(r'C:\Users\chamu\source\repos\EDUGuard_DesktopApp\EDUGuard_DesktopApp\PyFiles\posture_classifier.pkl')

# Nested deque to store 2-minute grouped outputs
posture_results = deque(maxlen=10)  # Store up to 10 batches of 2-minute outputs
current_batch = []  # Temporary list for storing 2-minute data

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Function to calculate the angle between two vectors
def calculate_angle(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)
    angle = np.arccos(dot_product / (magnitude1 * magnitude2))
    return np.degrees(angle)

# Function to update MongoDB with live posture data
def update_posture_in_mongodb(email, batch):
    try:
        # Find the user by email
        user = users_collection.find_one({"Email": email})
        if not user:
            print(f"User with email {email} not found!")
            return

        # Update posture data by appending the batch as a new list
        users_collection.update_one(
            {"Email": email},
            {"$push": {"PostureData": batch}}
        )
        print(f"Batch updated to MongoDB: {batch}")
    except Exception as e:
        print(f"Error updating posture data: {e}")

# Initialize webcam
cap = cv2.VideoCapture(0)

# Timer Setup
last_saved_time = time.time()
interval = 6  # Save data every 6 seconds
batch_interval = 30  # Upload batch data every 30 seconds
batch_start_time = time.time()

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from webcam.")
            break

        # Convert the frame to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process with Mediapipe
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Extract keypoints
            left_shoulder = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y)
            right_shoulder = (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y)
            nose = (landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                    landmarks[mp_pose.PoseLandmark.NOSE.value].y)

            # Get image dimensions
            h, w, _ = frame.shape

            # Convert to pixel coordinates
            left_shoulder = (int(left_shoulder[0] * w), int(left_shoulder[1] * h))
            right_shoulder = (int(right_shoulder[0] * w), int(right_shoulder[1] * h))
            nose = (int(nose[0] * w), int(nose[1] * h))

            # Calculate the midpoint
            mid_point = ((left_shoulder[0] + right_shoulder[0]) // 2,
                         (left_shoulder[1] + right_shoulder[1]) // 2)

            # Draw keypoints and lines
            cv2.line(frame, left_shoulder, right_shoulder, (0, 255, 0), 2)  # Green line
            cv2.line(frame, mid_point, nose, (0, 0, 255), 2)  # Red line

            # Calculate vectors
            green_line = np.array(right_shoulder) - np.array(left_shoulder)
            red_line = np.array([1, 0])
            blue_line = np.array(nose) - np.array([(left_shoulder[0] + right_shoulder[0]) / 2,
                                                   (left_shoulder[1] + right_shoulder[1]) / 2])

            # Calculate angles
            angle_red_green = calculate_angle(red_line, green_line)
            angle_blue_green = calculate_angle(blue_line, green_line)

            # Prepare features for prediction
            features = np.array([[angle_red_green, angle_blue_green]])

            # Predict posture
            prediction = model.predict(features)
            posture = "Good Posture" if prediction[0] == 1 else "Bad Posture"

            # Display the prediction
            cv2.putText(frame, f"Posture: {posture}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Save posture result to the current batch every 6 seconds
            current_time = time.time()
            if current_time - last_saved_time >= interval:
                current_batch.append(posture)
                print(f"Saved posture: {posture}")
                last_saved_time = current_time

        # Upload batch to MongoDB every 30 seconds
        if current_time - batch_start_time >= batch_interval:
            if current_batch:  # Check if the batch is not empty
                update_posture_in_mongodb(USER_EMAIL, current_batch)
                current_batch = []  # Reset batch
            batch_start_time = current_time

        # Show the frame
        cv2.imshow('Posture Detection', frame)

        # Exit on pressing 'q'
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

finally:
    # Save any remaining data to MongoDB before exit
    if current_batch:
        update_posture_in_mongodb(USER_EMAIL, current_batch)

    cap.release()
    cv2.destroyAllWindows()
