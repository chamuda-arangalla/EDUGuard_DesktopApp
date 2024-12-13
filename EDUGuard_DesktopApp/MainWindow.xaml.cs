using System.Windows;
using EDUGuard_DesktopApp.Views;

namespace EDUGuard_DesktopApp
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            LoadLoginView();
        }

        private void LoadLoginView()
        {
            var loginView = new LoginView();
            loginView.NavigateToSignUpEvent += (s, e) => LoadSignUpView();
            MainContent.Content = loginView;
        }

        private void LoadSignUpView()
        {
            var signUpView = new SignUpView();
            signUpView.NavigateToLoginEvent += (s, e) => LoadLoginView();
            MainContent.Content = signUpView;
        }
    }
}
