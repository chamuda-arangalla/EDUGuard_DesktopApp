using System.Diagnostics;
using System;
using System.IO;
using System.Text.Json;
using System.Windows;
using EDUGuard_DesktopApp.Models;
using EDUGuard_DesktopApp.Utilities;
using MongoDB.Driver;
using System.Linq;
using System.Collections.Generic;

namespace EDUGuard_DesktopApp.Views
{
    public partial class DashboardView : Window
    {
        private readonly DatabaseHelper _dbHelper = new DatabaseHelper();

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
            var processInfo = new ProcessStartInfo
            {
                FileName = @"C:\Users\chamu\AppData\Local\Microsoft\WindowsApps\python.exe",
                Arguments = @"C:\Users\chamu\source\repos\EDUGuard_DesktopApp\EDUGuard_DesktopApp\PyFiles\posture_detection.py",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            try
            {
                using (var process = Process.Start(processInfo))
                {
                    if (process == null)
                    {
                        MessageBox.Show("Failed to start the Python process.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                        return;
                    }

                    // Read output and error asynchronously
                    var outputTask = process.StandardOutput.ReadToEndAsync();
                    var errorTask = process.StandardError.ReadToEndAsync();

                    process.WaitForExit();

                    string output = outputTask.Result;
                    string error = errorTask.Result;

                    if (!string.IsNullOrEmpty(error))
                    {
                        MessageBox.Show($"Python Error:\n{error}", "Python Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    }

                    if (File.Exists("posture_results.json"))
                    {
                        string json = File.ReadAllText("posture_results.json");

                        try
                        {
                            // Deserialize into List<List<string>>
                            var postureResults = JsonSerializer.Deserialize<List<List<string>>>(json);

                            if (postureResults != null && postureResults.Any(batch => batch.Count > 0))
                            {
                                SavePostureResults(postureResults);

                                MessageBox.Show("Posture Detection Complete! Data saved successfully.", "Success",
                                                MessageBoxButton.OK, MessageBoxImage.Information);
                            }
                            else
                            {
                                MessageBox.Show("No valid posture data found in the JSON file.", "Warning",
                                                MessageBoxButton.OK, MessageBoxImage.Warning);
                            }
                        }
                        catch (JsonException ex)
                        {
                            MessageBox.Show($"JSON Parsing Error: {ex.Message}\nRaw JSON Content:\n{json}", "Error",
                                            MessageBoxButton.OK, MessageBoxImage.Error);
                        }
                    }
                    else
                    {
                        MessageBox.Show("Posture results file not found.", "Error",
                                        MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }





        /// <summary>
        /// Saves posture results to MongoDB.
        /// </summary>
       private void SavePostureResults(List<List<string>> batches)
        {
            var filter = Builders<User>.Filter.Eq(u => u.Email, SessionManager.CurrentUser.Email);

            if (batches == null || batches.Count == 0)
            {
                MessageBox.Show("No valid posture data to save!", "Warning", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            // Push the entire list of batches into the PostureData array
            var update = Builders<User>.Update.PushEach("PostureData", batches);

            var result = _dbHelper.Users.UpdateOne(filter, update);

            if (result.MatchedCount == 0)
            {
                MessageBox.Show("User not found!", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            else if (result.ModifiedCount == 0)
            {
                MessageBox.Show("Failed to save posture results!", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            else
            {
                MessageBox.Show("Posture results saved successfully!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }





    }

    
}
