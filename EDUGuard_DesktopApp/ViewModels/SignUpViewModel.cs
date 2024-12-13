using EDUGuard_DesktopApp.Models;
using EDUGuard_DesktopApp.Utilities;
using MongoDB.Driver;
using System.Windows;
using System.Windows.Controls;

namespace EDUGuard_DesktopApp.Views
{
    public partial class SignUpView : UserControl
    {
        public event RoutedEventHandler NavigateToLoginEvent;

        public SignUpView()
        {
            InitializeComponent();
        }

        private void SignUpButton_Click(object sender, RoutedEventArgs e)
        {
            string firstName = FirstNameTextBox.Text;
            string lastName = LastNameTextBox.Text;
            string ageText = AgeTextBox.Text;
            string email = EmailTextBox.Text;
            string password = SignUpPasswordBox.Password;

            if (string.IsNullOrWhiteSpace(firstName) || string.IsNullOrWhiteSpace(lastName) ||
                string.IsNullOrWhiteSpace(ageText) || string.IsNullOrWhiteSpace(email) || string.IsNullOrWhiteSpace(password))
            {
                MessageBox.Show("All fields are required.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            if (!int.TryParse(ageText, out int age) || age <= 0)
            {
                MessageBox.Show("Age must be a valid number greater than 0.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            var dbHelper = new DatabaseHelper();
            var existingUser = dbHelper.Users.Find(u => u.Email == email).FirstOrDefault();

            if (existingUser != null)
            {
                MessageBox.Show("A user with this email already exists.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            var user = new User
            {
                FirstName = firstName,
                LastName = lastName,
                Age = age,
                Email = email,
                Password = PasswordHelper.HashPassword(password)
            };

            dbHelper.Users.InsertOne(user);
            MessageBox.Show("Sign-Up successful!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);

            NavigateToLoginEvent?.Invoke(this, new RoutedEventArgs());
        }

        private void NavigateToLogin(object sender, RoutedEventArgs e)
        {
            NavigateToLoginEvent?.Invoke(this, new RoutedEventArgs());
        }
    }
}
