using System.Diagnostics;
using System;
using System.IO;
using System.Windows;
using EDUGuard_DesktopApp.Models;
using EDUGuard_DesktopApp.Utilities;
using MongoDB.Driver;
using System.Windows.Media;
using System.Threading.Tasks;

namespace EDUGuard_DesktopApp.Views
{
    public partial class DashboardView : Window
    {
        private readonly DatabaseHelper _dbHelper = new DatabaseHelper();
        private Process _pythonProcess; // Tracks the Python process
        private bool _isRunning = false; // Tracks the state (Start/Stop)

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
            LoadUserProfile();
        }

        /// <summary>
        /// Logs out the current user.
        /// </summary>
        private void LogoutButton_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show("Are you sure you want to log out?", "Logout Confirmation",
                                         MessageBoxButton.YesNo, MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                SessionManager.EndSession();
                this.Close();
                var mainWindow = new MainWindow();
                mainWindow.Show();
            }
        }

        /// <summary>
        /// Opens Settings.
        /// </summary>
        private void SettingsButton_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Settings functionality is under development.", "Settings",
                            MessageBoxButton.OK, MessageBoxImage.Information);
        }

        /// <summary>
        /// Loads the current user's profile details.
        /// </summary>
        private void LoadUserProfile()
        {
            var user = SessionManager.CurrentUser;
            if (user != null)
            {
                FirstNameTextBox.Text = user.FirstName;
                LastNameTextBox.Text = user.LastName;
                EmailTextBox.Text = user.Email;
                AgeTextBox.Text = user.Age.ToString();
                ContactNumberTextBox.Text = user.ContactNumber;
            }
        }

        /// <summary>
        /// Updates the current user's profile.
        /// </summary>
        private void UpdateButton_Click(object sender, RoutedEventArgs e)
        {
            var updatedUser = SessionManager.CurrentUser;
            updatedUser.FirstName = FirstNameTextBox.Text;
            updatedUser.LastName = LastNameTextBox.Text;
            updatedUser.ContactNumber = ContactNumberTextBox.Text;

            if (int.TryParse(AgeTextBox.Text, out int updatedAge))
            {
                updatedUser.Age = updatedAge;
            }
            else
            {
                MessageBox.Show("Invalid Age value. Please enter a valid number.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            var filter = Builders<User>.Filter.Eq(u => u.Email, updatedUser.Email);
            var update = Builders<User>.Update
                .Set(u => u.FirstName, updatedUser.FirstName)
                .Set(u => u.LastName, updatedUser.LastName)
                .Set(u => u.ContactNumber, updatedUser.ContactNumber)
                .Set(u => u.Age, updatedUser.Age);

            _dbHelper.Users.UpdateOne(filter, update);

            MessageBox.Show("Profile updated successfully!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        /// <summary>
        /// Deletes the current user's account.
        /// </summary>
        private void DeleteButton_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show("Are you sure you want to delete your account? This action is irreversible.",
                                         "Confirm Delete", MessageBoxButton.YesNo, MessageBoxImage.Warning);

            if (result == MessageBoxResult.Yes)
            {
                var filter = Builders<User>.Filter.Eq(u => u.Email, SessionManager.CurrentUser.Email);
                _dbHelper.Users.DeleteOne(filter);

                MessageBox.Show("Account deleted successfully.", "Account Deleted", MessageBoxButton.OK, MessageBoxImage.Information);

                SessionManager.EndSession();
                Close();
                var loginView = new MainWindow();
                loginView.Show();
            }
        }

        /// <summary>
        /// Runs the Python script for posture detection.
        /// </summary>
        private void RunPostureDetection_Click(object sender, RoutedEventArgs e)
        {
            if (!_isRunning)
            {
                StartPythonProcess();
            }
            else
            {
                StopPythonProcess();
            }
        }

        private void StartPythonProcess()
        {
            var userEmail = SessionManager.CurrentUser.Email; // Get the authenticated user's email from the session

            var processInfo = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"C:\\Users\\chamu\\source\\repos\\EDUGuard_DesktopApp\\EDUGuard_DesktopApp\\PyFiles\\posture_detection.py {userEmail}",
                UseShellExecute = false, // Required for redirection
                RedirectStandardOutput = true, // Capture Python output
                RedirectStandardError = true,  // Capture Python errors
                CreateNoWindow = true // Run in the background
            };

            try
            {
                _pythonProcess = Process.Start(processInfo);

                if (_pythonProcess == null)
                {
                    MessageBox.Show("Failed to start the Python process.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }

                _isRunning = true;
                UpdateButtonUI(_isRunning);

                Task.Run(() => ReadStreamAsync(_pythonProcess.StandardOutput, line =>
                {
                    Dispatcher.Invoke(() => Console.WriteLine($"[Output]: {line}"));
                }));

                Task.Run(() => ReadStreamAsync(_pythonProcess.StandardError, line =>
                {
                    Dispatcher.Invoke(() => Console.WriteLine($"[Error]: {line}"));
                }));

                Task.Run(() =>
                {
                    _pythonProcess.WaitForExit();
                    Dispatcher.Invoke(() =>
                    {
                        _isRunning = false;
                        UpdateButtonUI(_isRunning);
                        MessageBox.Show("Python process completed successfully.", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
                    });
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred while starting the Python process: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private Task ReadStreamAsync(StreamReader reader, Action<string> onLineRead)
        {
            return Task.Run(async () =>
            {
                try
                {
                    string line;
                    while ((line = await reader.ReadLineAsync()) != null)
                    {
                        onLineRead(line); // Collect lines without invoking Dispatcher
                    }
                }
                catch (Exception ex)
                {
                    Dispatcher.Invoke(() =>
                    {
                        MessageBox.Show($"Error reading stream: {ex.Message}", "Stream Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    });
                }
            });
        }

        private void StopPythonProcess()
        {
            try
            {
                if (_pythonProcess != null && !_pythonProcess.HasExited)
                {
                    _pythonProcess.Kill();
                    _pythonProcess.Dispose();
                }

                _isRunning = false;
                UpdateButtonUI(_isRunning);

            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to stop the Python process: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void UpdateButtonUI(bool isRunning)
        {
            if (isRunning)
            {
                RunPostureDetection.Content = "Stop";
                RunPostureDetection.Background = Brushes.LightCoral;
                RunPostureDetection.Foreground = Brushes.White;
            }
            else
            {
                RunPostureDetection.Content = "Start";
                RunPostureDetection.Background = Brushes.LightGreen;
                RunPostureDetection.Foreground = Brushes.Black;
            }
        }
    }
}
