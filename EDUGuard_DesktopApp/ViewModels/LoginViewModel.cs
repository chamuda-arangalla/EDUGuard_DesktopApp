using EDUGuard_DesktopApp.Utilities;
using MongoDB.Driver;
using System.Windows;
using System.Windows.Controls;

namespace EDUGuard_DesktopApp.Views
{
    public partial class LoginView : UserControl
    {
        public event RoutedEventHandler NavigateToSignUpEvent;

        public LoginView()
        {
            InitializeComponent();
        }

        private void LoginButton_Click(object sender, RoutedEventArgs e)
        {
            string username = UsernameTextBox.Text;
            string password = PasswordBox.Password;

            var dbHelper = new DatabaseHelper();
            var user = dbHelper.Users.Find(u => u.Email == username).FirstOrDefault();

            if (user != null && PasswordHelper.VerifyPassword(user.Password, password))
            {
                MessageBox.Show("Login successful!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);

                // Navigate to dashboard or application home
            }
            else
            {
                MessageBox.Show("Invalid credentials!", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void NavigateToSignUp(object sender, RoutedEventArgs e)
        {
            NavigateToSignUpEvent?.Invoke(this, new RoutedEventArgs());
        }
    }
}
