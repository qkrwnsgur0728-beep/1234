using System.Windows;
using AMPManager.View;
using AMPManager.ViewModel;

namespace AMPManager
{
    public partial class App : System.Windows.Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // 1. 로그인 창 띄우기
            LoginWindow loginWindow = new LoginWindow();
            bool? result = loginWindow.ShowDialog();

            // 2. 로그인 성공 시
            if (result == true)
            {
                var loginVM = loginWindow.DataContext as LoginViewModel;
                var user = loginVM?.LoggedInUser;

                if (user != null)
                {
                    // 메인 화면 생성
                    MainWindow mainWindow = new MainWindow();
                    var mainVM = new MainViewModel(user);
                    mainWindow.DataContext = mainVM;

                    // [중요] 메인 윈도우를 앱의 주인으로 설정
                    this.MainWindow = mainWindow;

                    // 메인 화면 띄우기
                    mainWindow.Show();

                    // [중요] 이제부터는 "메인 화면이 닫히면 앱을 종료해라"로 설정 변경
                    this.ShutdownMode = ShutdownMode.OnMainWindowClose;
                }
                else
                {
                    Shutdown();
                }
            }
            else
            {
                // 로그인 실패/취소 시 종료
                Shutdown();
            }
        }
    }
}