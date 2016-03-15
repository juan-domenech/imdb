from Tkinter import *
import os
from database.mysql import MySQLDatabase

DEBUG = 0


db = MySQLDatabase('imdb','imdb','imdb','localhost')

root = Tk()

search = ''

def key(event):
    global search
    os.system('clear')
    key = repr(event.char)
    if DEBUG == 1:
        print "pressed1:",key[0:1]
        print "pressed2:",key[1:2]
        print "pressed3:",key[2:3]
        print "pressed4:",key[3:4]
        print "pressed4:",key[4:5]
    print
    # Backspace
    if key[2:5] == 'x7f':
        search = search[:-1]
    # Invalind key
    elif key == '' or key == "''":
        pass
    # Add to the string
    else:
        search = search + key[1]
    print "Search: *"+search+"*"
    if search != '' and search != "''" and search[:-1] != "'":
        movies = db.search(search)
        print
        for movie in movies:
            print movie
    else:
        print "Search includes trash:"+search

def callback(event):
    frame.focus_set()
    #print "clicked at", event.x, event.y

frame = Frame(root, width=100, height=100)
frame.bind("<Key>", key)
frame.bind("<Button-1>", callback)
frame.pack()

root.mainloop()
