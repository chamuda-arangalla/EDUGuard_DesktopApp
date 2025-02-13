﻿using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using EDUGuard_DesktopApp.Models;
using EDUGuard_DesktopApp.Utilities;
using MongoDB.Driver;
using System.Linq;
using System.Timers;
using MongoDB.Bson;

namespace EDUGuard_DesktopApp.Views
{
    public partial class DashboardView : Window
    {
        private readonly DatabaseHelper _dbHelper = new DatabaseHelper();
        private readonly Dictionary<string, Process> _modelProcesses = new Dictionary<string, Process>();
        private Process _webcamServerProcess;
        private bool _isModel1Running = false, _isModel2Running = false, _isModel3Running = false, _isModel4Running = false;
        private readonly string _currentUserEmail;
        private Timer _alertTimer;
        private readonly string _logFilePath = "C:\\Users\\chamu\\source\\repos\\EDUGuard_DesktopApp\\error_log.txt";

        public DashboardView()
        {
            if (!SessionManager.IsLoggedIn)
            {
                LogError("Access Denied: User not logged in.");
                Close();
                return;
            }
        

            InitializeComponent();
            StartWebcamServer();
            LoadUserProfile();

            // Get the current user's email
            _currentUserEmail = SessionManager.CurrentUser?.Email;
            if (string.IsNullOrEmpty(_currentUserEmail))
            {
                LogError("Failed to retrieve the user's email.");
                Close();
            }


            }

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

        private void StartWebcamServer()
        {
            var processInfo = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = "C:\\Users\\chamu\\source\\repos\\EDUGuard_DesktopApp\\EDUGuard_DesktopApp\\PyFiles\\webcam_server.py",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            try
            {
                _webcamServerProcess = Process.Start(processInfo);
                if (_webcamServerProcess == null)
                {
                    LogError("Failed to start the webcam server.");
                }
            }
            catch (Exception ex)
            {
                LogError($"Error starting the webcam server: {ex.Message}");
            }
        }

        //private void ClearPostureDataInDatabase()
        //{
        //    try
        //    {
        //        var filter = Builders<User>.Filter.Eq(u => u.Email, _currentUserEmail);
        //        var update = Builders<User>.Update.Set(u => u.PostureData, new List<List<string>>());

        //        _dbHelper.Users.UpdateOne(filter, update);
        //    }
        //    catch (Exception ex)
        //    {
        //        LogError($"Error clearing posture data: {ex.Message}");
        //    }
        //}

        private void ToggleModel(string modelName, ref bool isRunning, Button modelButton, string scriptPath)
        {
            if (!isRunning)
            {
                StartModel(modelName, ref isRunning, modelButton, scriptPath);
            }
            else
            {
                StopModel(modelName, ref isRunning, modelButton);
            }
        }

        //private void StartModel(string modelName, ref bool isRunning, Button modelButton, string scriptPath)
        //{
        //    var processInfo = new ProcessStartInfo
        //    {
        //        FileName = "python",
        //        Arguments = $"{scriptPath} {_currentUserEmail}",
        //        UseShellExecute = false,
        //        RedirectStandardOutput = true,
        //        RedirectStandardError = true,
        //        CreateNoWindow = true
        //    };

        //    try
        //    {
        //        var process = Process.Start(processInfo);
        //        if (process == null)
        //        {
        //            LogError($"Failed to start {modelName}.");
        //            return;
        //        }

        //        _modelProcesses[modelName] = process;
        //        UpdateButtonUI(modelButton, true, $"Start {modelName}", $"Stop {modelName}");

        //        Task.Run(() =>
        //        {
        //            ReadStreamAsync(process.StandardOutput, line => Console.WriteLine($"[{modelName} Output]: {line}"));
        //            ReadStreamAsync(process.StandardError, line => LogError($"[{modelName} Error]: {line}"));
        //        });

        //        isRunning = true;
        //        //StartPostureMonitoring();
        //    }
        //    catch (Exception ex)
        //    {
        //        LogError($"Error starting {modelName}: {ex.Message}");
        //    }
        //}

        private void StartModel(string modelName, ref bool isRunning, Button modelButton, string scriptPath)
        {
            var startTime = DateTime.UtcNow;
            var progressReportId = _dbHelper.CreateProgressReport(_currentUserEmail, modelName, startTime);

            if (string.IsNullOrEmpty(progressReportId))
            {
                LogError($"Failed to create progress report for {modelName}.");
                return;
            }

            var processInfo = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"{scriptPath} {_currentUserEmail} {progressReportId}", // Pass progressReportId
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            try
            {
                var process = Process.Start(processInfo);
                if (process == null)
                {
                    LogError($"Failed to start {modelName}.");
                    return;
                }

                _modelProcesses[modelName] = process;
                UpdateButtonUI(modelButton, true, $"Start {modelName}", $"Stop {modelName}");

                Task.Run(() =>
                {
                    ReadStreamAsync(process.StandardOutput, line => Console.WriteLine($"[{modelName} Output]: {line}"));
                    ReadStreamAsync(process.StandardError, line => LogError($"[{modelName} Error]: {line}"));
                });

                isRunning = true;
            }
            catch (Exception ex)
            {
                LogError($"Error starting {modelName}: {ex.Message}");
            }
        }


        private void StopModel(string modelName, ref bool isRunning, Button modelButton)
        {
            try
            {
                if (_modelProcesses.ContainsKey(modelName))
                {
                    var process = _modelProcesses[modelName];
                    if (!process.HasExited)
                    {
                        process.Kill();
                        process.Dispose();
                    }
                    _modelProcesses.Remove(modelName);

                    //ClearPostureDataInDatabase();

                    UpdateButtonUI(modelButton, false, $"Start {modelName}", $"Stop {modelName}");
                    isRunning = false;
                }
            }
            catch (Exception ex)
            {
                LogError($"Error stopping {modelName}: {ex.Message}");
            }
        }

        private void UpdateButtonUI(Button button, bool isRunning, string startText, string stopText)
        {
            button.Content = isRunning ? stopText : startText;
            button.Background = isRunning ? Brushes.LightCoral : Brushes.LightGreen;
            button.Foreground = isRunning ? Brushes.White : Brushes.Black;
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
        /// Opens Settings.
        /// </summary>
        private void SettingsButton_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Settings functionality is under development.", "Settings",
                            MessageBoxButton.OK, MessageBoxImage.Information);
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
        private Task ReadStreamAsync(StreamReader reader, Action<string> onLineRead)
        {
            return Task.Run(async () =>
            {
                try
                {
                    string line;
                    while ((line = await reader.ReadLineAsync()) != null)
                    {
                        onLineRead(line);
                    }
                }
                catch (Exception ex)
                {
                    LogError($"Stream read error: {ex.Message}");
                }
            });
        }

        private void Model1Button_Click(object sender, RoutedEventArgs e)
        {
            ToggleModel("Model1", ref _isModel1Running, (Button)sender, "C:\\Users\\chamu\\source\\repos\\EDUGuard_DesktopApp\\EDUGuard_DesktopApp\\PyFiles\\posture_detection1.py");
        }

        private void Model2Button_Click(object sender, RoutedEventArgs e)
        {
            ToggleModel("Model2", ref _isModel2Running, (Button)sender, "C:\\Users\\chamu\\source\\repos\\EDUGuard_DesktopApp\\EDUGuard_DesktopApp\\PyFiles\\stress_detection.py");
        }

        private void Model3Button_Click(object sender, RoutedEventArgs e)
        {
            ToggleModel("Model3", ref _isModel3Running, (Button)sender, "C:\\Users\\chamu\\source\\repos\\EDUGuard_DesktopApp\\EDUGuard_DesktopApp\\PyFiles\\model3.py");
        }

        private void Model4Button_Click(object sender, RoutedEventArgs e)
        {
            ToggleModel("Model4", ref _isModel4Running, (Button)sender, "C:\\Users\\chamu\\source\\repos\\EDUGuard_DesktopApp\\EDUGuard_DesktopApp\\PyFiles\\model4.py");
        }

        //private void StartPostureMonitoring()
        //{
        //    _alertTimer = new Timer(30000); // Check every 30 seconds
        //    _alertTimer.Elapsed += CheckPostureAlerts;
        //    _alertTimer.AutoReset = true;
        //    _alertTimer.Start();
        //}

        //private async void CheckPostureAlerts(object sender, ElapsedEventArgs e)
        //{
        //    try
        //    {
        //        var filter = Builders<User>.Filter.Eq(u => u.Email, _currentUserEmail);
        //        var user = await _dbHelper.Users.Find(filter).FirstOrDefaultAsync();

        //        if (user != null && user.PostureData != null)
        //        {
        //            // Flatten the 2D array
        //            var allPostureData = user.PostureData.SelectMany(array => array).ToList();

        //            // Calculate percentage of "Bad Posture"
        //            int badPostureCount = allPostureData.Count(p => p == "Bad Posture");
        //            int totalCount = allPostureData.Count;

        //            if (totalCount > 0)
        //            {
        //                double badPosturePercentage = (double)badPostureCount / totalCount * 100;

        //                // Show alert if bad posture exceeds 70%
        //                if (badPosturePercentage > 70)
        //                {
        //                    Dispatcher.Invoke(() =>
        //                    {
        //                        MessageBox.Show($"Alert! Your posture quality is poor: {badPosturePercentage:F1}% bad posture detected.",
        //                            "Posture Alert", MessageBoxButton.OK, MessageBoxImage.Warning);
        //                    });
        //                }
        //            }
        //        }
        //    }
        //    catch (Exception ex)
        //    {
        //        Dispatcher.Invoke(() =>
        //        {
        //            MessageBox.Show($"Error checking posture alerts: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
        //        });
        //    }
        //}


        protected override void OnClosed(EventArgs e)
        {
            _alertTimer?.Stop();
            _alertTimer?.Dispose();
            base.OnClosed(e);
        }


        private void LogoutButton_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show("Are you sure you want to log out?", "Logout Confirmation",
                             MessageBoxButton.YesNo, MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                SessionManager.EndSession();
                StopAllProcesses();
                Close();
                var mainWindow = new MainWindow();
                mainWindow.Show();
            }
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            StopAllProcesses();
        }

        private void StopAllProcesses()
        {
            foreach (var modelName in _modelProcesses.Keys)
            {
                try
                {
                    var process = _modelProcesses[modelName];
                    if (!process.HasExited)
                    {
                        process.Kill();
                        process.Dispose();
                    }
                }
                catch (Exception ex)
                {
                    LogError($"Error stopping {modelName}: {ex.Message}");
                }
            }

            if (_webcamServerProcess != null && !_webcamServerProcess.HasExited)
            {
                try
                {
                    _webcamServerProcess.Kill();
                    _webcamServerProcess.Dispose();
                }
                catch (Exception ex)
                {
                    LogError($"Error stopping Webcam Server: {ex.Message}");
                }
            }
        }

        private void LogError(string message)
        {
            try
            {
                string logMessage = $"{DateTime.Now}: {message}\n";
                File.AppendAllText(_logFilePath, logMessage);
            }
            catch
            {
                // Avoid crashes if logging fails
            }
        }
    }

 
}
