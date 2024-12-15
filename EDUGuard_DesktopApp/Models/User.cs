using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace EDUGuard_DesktopApp.Models
{
    public class User
    {
        [BsonId] // Indicates this is the MongoDB _id field
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; } // MongoDB ObjectId stored as a string
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public int Age { get; set; }
        public string Email { get; set; } // Used as the username
        public string Password { get; set; }
        public string ContactNumber { get; set; }
    }
}
