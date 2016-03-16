# http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
from Tkinter import *
import os
import time

root = Tk()


def key(event):
    os.system('clear')
    print "pressed", repr(event.char)

    for i in range(0,50):
        print "***",i

    time.sleep(10)

def callback(event):
    frame.focus_set()
    print "clicked at", event.x, event.y

frame = Frame(root, width=100, height=100)
frame.bind("<Key>", key)
frame.bind("<Button-1>", callback)
frame.pack()

root.mainloop()