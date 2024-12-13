using EDUGuard_DesktopApp.Models;
using MongoDB.Driver;

namespace EDUGuard_DesktopApp
{
    public class DatabaseHelper
    {
        private readonly IMongoDatabase _database;

        public DatabaseHelper()
        {
            // Replace with your MongoDB Atlas connection string
            var connectionString = "mongodb+srv://myUser:myPassword123@cluster0.qk0epky.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
            var client = new MongoClient(connectionString);
            _database = client.GetDatabase("EDUGuardDB");
        }

        public IMongoCollection<User> Users => _database.GetCollection<User>("Users");

        
    }
}
