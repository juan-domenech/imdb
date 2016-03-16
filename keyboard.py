# http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
from Tkinter import *
import os
from database.mysql import MySQLDatabase

from database.ranking import basic_ranking

DEBUG = 0

red_light = False

db = MySQLDatabase('imdb','imdb','imdb','localhost')

root = Tk()

search = ''


def key(event):
    global search
    global red_light
    os.system('clear')
    key = repr(event.char)
    if DEBUG == 1:
        print "pressed1:",key[0:1]
        print "pressed2:",key[1:2]
        print "pressed3:",key[2:3]
        print "pressed4:",key[3:4]
        print "pressed4:",key[4:5]

    # Backspace
    if key[2:5] == 'x7f':
        search = search[:-1]
    # Invalind key
    elif key == '' or key == "''":
        pass
    elif key[2] == 'r':
        red_light = False
    # Add to the string
    else:
        search = search + key[1]
    print "Search: *"+search+"*",red_light

    if search != '' and search != "''" and search[:-1] != "'" :
        # It looks OK. Let's search...
        if red_light == False :
            red_light = True
            print "Connecting to IMDB..."
            movies = db.search(search)
            red_light = False
            movies = basic_ranking(movies)
            if len(movies):
                #print "\b" * 21,
                for movie in range(0,len(movies)):
                    print movies[movie]['title'], "("+str(movies[movie]['year'])+")"
            else:
                print "No matches..."
    else:
        print "Search includes trash:",search

def callback(event):
    frame.focus_set()
    #print "clicked at", event.x, event.y

frame = Frame(root, width=100, height=100)
frame.bind("<Key>", key)
frame.bind("<Button-1>", callback)
frame.pack()

root.mainloop()
