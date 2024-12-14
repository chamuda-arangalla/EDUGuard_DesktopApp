using System.Windows;
using EDUGuard_DesktopApp.Utilities;

namespace EDUGuard_DesktopApp.Views
{
    public partial class DashboardView : Window
    {
        public DashboardView()
        {
            // Validate the session
            if (!SessionManager.IsLoggedIn)
            {
                MessageBox.Show("You are not authorized to access this window. Please log in.", "Access Denied",
                                MessageBoxButton.OK, MessageBoxImage.Warning);
                Close();
                return;
            }

            InitializeComponent();
        }

        private void SettingsButton_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Settings functionality is under development.", "Settings",
                            MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}
