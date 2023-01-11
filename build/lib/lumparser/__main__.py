"""Execute this file to run the LumParsing user interface"""

from lumparser.user_interface.mainwindow import App

if __name__ == "__main__":
    app = App()
    app.mainloop()  # initialize event loop (start interaction with user)
