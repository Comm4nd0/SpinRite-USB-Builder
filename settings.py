def init():
    global ICON
    ICON = 'sr.gif'

def center(master, win, width, height):
    """center the window on the screen"""
    # get screen width and height
    ws = master.winfo_screenwidth()  # width of the screen
    hs = master.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws / 2) - (width / 2)
    y = (hs / 2) - (height / 2)

    return width, height, x, y