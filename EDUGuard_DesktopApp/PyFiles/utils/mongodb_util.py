from pymongo import MongoClient

# MongoDB connection setup
MONGO_URI = "mongodb+srv://myUser:myPassword123@cluster0.qk0epky.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["EDUGuardDB"]  
users_collection = db["Users"]  

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
