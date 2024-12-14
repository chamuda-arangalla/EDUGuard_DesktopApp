using EDUGuard_DesktopApp.Models;

namespace EDUGuard_DesktopApp.Utilities
{
    public static class SessionManager
    {
        public static User CurrentUser { get; private set; }

        public static bool IsLoggedIn => CurrentUser != null;

        public static void StartSession(User user)
        {
            CurrentUser = user;
        }

        public static void EndSession()
        {
            CurrentUser = null;
        }
    }
}
