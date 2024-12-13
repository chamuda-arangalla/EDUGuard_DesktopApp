using System;
using System.Security.Cryptography;
using System.Text;

namespace EDUGuard_DesktopApp.Utilities
{
    public static class PasswordHelper
    {
        /// <summary>
        /// Hashes the given password using SHA256.
        /// </summary>
        /// <param name="password">The plain text password to hash.</param>
        /// <returns>The hashed password as a Base64 string.</returns>
        public static string HashPassword(string password)
        {
            using (var sha256 = SHA256.Create())
            {
                var bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(password));
                return Convert.ToBase64String(bytes);
            }
        }

        /// <summary>
        /// Verifies if the provided plain text password matches the hashed password.
        /// </summary>
        /// <param name="hashedPassword">The hashed password stored in the database.</param>
        /// <param name="plainPassword">The plain text password to verify.</param>
        /// <returns>True if the password matches; otherwise, false.</returns>
        public static bool VerifyPassword(string hashedPassword, string plainPassword)
        {
            return hashedPassword == HashPassword(plainPassword);
        }
    }
}
