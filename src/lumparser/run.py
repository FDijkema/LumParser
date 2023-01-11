"""GUI entrypoint to run program"""

from lumparser.user_interface.mainwindow import App


def run_app():
    app = App()
    app.mainloop()  # initialize event loop (start interaction with user)
