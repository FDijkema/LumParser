"""Execute this file to run the LumParsing user interface"""

from lumparser.user_interface.mainwindow import App
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'LumParser-1.0.0'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


if __name__ == "__main__":
    app = App()
    app.mainloop()  # initialize event loop (start interaction with user)
