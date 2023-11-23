# Elmo GUI

import tkinter as tk

root = tk.Tk()

# place a label on the root window
root.geometry('400x500+50+50')
root.title('Ground Control System')
message = tk.Label(root, text=roll)
message.pack()


# keep the window displaying
root.mainloop()
