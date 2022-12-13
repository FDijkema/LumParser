"""Execute this file to run the LumParsing user interface"""

from src.user_interface import mainwindow

app = mainwindow.App()
app.mainloop()  # initialize event loop (start interaction with user)
app.quit()
quit()
