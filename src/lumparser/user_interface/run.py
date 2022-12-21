"""Execute this file to run the LumParsing user interface"""
from .mainwindow import App


def run_app():
    app = App()
    app.mainloop()  # initialize event loop (start interaction with user)
    app.quit()
    quit()
