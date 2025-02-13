from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection setup
MONGO_URI = "mongodb+srv://myUser:myPassword123@cluster0.qk0epky.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["EDUGuardDB"]  
users_collection = db["Users"]  
progress_reports_collection = db["ProgressReports"]

def authenticate_user(email):
    """
    Authenticate the user by email.
    :param email: User's email address.
    :return: User document if found, otherwise None.
    """
    try:
        user = users_collection.find_one({"Email": email})
        if user:
            return user
        else:
            print(f"User with email {email} not found.")
            return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def save_posture_data(email, posture_data):
    """
    Save posture data to the user's record in MongoDB.
    :param email: User's email address.
    :param posture_data: Posture data to save.
    """
    try:
        user = authenticate_user(email)
        if not user:
            return

        users_collection.update_one(
            {"Email": email},
            {"$push": {"PostureData": posture_data}}
        )
        print(f"Saved posture data for {email}: {posture_data}")
    except Exception as e:
        print(f"Error saving posture data: {e}")

def save_stress_data(email, stress_data):
    """
    Save posture data to the user's record in MongoDB.
    :param email: User's email address.
    :param stress_data: Stress data to save.
    """
    try:
        user = authenticate_user(email)
        if not user:
            return

        users_collection.update_one(
            {"Email": email},
            {"$push": {"StressData": stress_data}}
        )
        print(f"Saved stress data for {email}: {stress_data}")
    except Exception as e:
        print(f"Error saving stress data: {e}")

def update_posture_outputs(progress_report_id, new_outputs):
    """
    Updates only the 'outputs' array in PostureData for an existing ProgressReports document.
    :param progress_report_id: The ID of the progress report to update.
    :param new_outputs: The new posture output data to be appended.
    """
    try:
        # Convert the string ID to an ObjectId
        object_id = ObjectId(progress_report_id)

        update_query = {
            "$push": {
                "PostureData.Outputs": {"$each": [new_outputs]}  # Append new outputs to existing array
            }
        }

        result = progress_reports_collection.update_one({"_id": object_id}, update_query)

        if result.matched_count > 0:
            print(f"Successfully updated 'outputs' for Progress Report ID: {progress_report_id}")
        else:
            print(f"Progress report with ID {progress_report_id} not found.")

    except Exception as e:
        print(f"Error updating progress report: {e}")
