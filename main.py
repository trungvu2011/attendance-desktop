import sys
from PyQt5.QtWidgets import QApplication
from app.views.main_window import MainWindow
from app.controllers.auth_controller import AuthController

if __name__ == "__main__":
    print("Starting Attendance Management System...")
    try:
        app = QApplication(sys.argv)
        print("Application instance created")
        
        auth_controller = AuthController()
        print("Auth controller initialized")
        
        main_window = MainWindow(auth_controller)
        print("Main window created")
        
        # Make sure the window is shown
        main_window.show()
        print("Main window displayed")
        
        print("Entering application event loop")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()