from database.mysql import MySQLDatabase
from database.ranking import basic_ranking

db = MySQLDatabase('imdb','imdb','imdb','localhost')

DEBUG = 0

movies = db.search('gon')

print "Main:"
print len(movies)
for movie in sorted(movies):
    print movie


#movies_new = basic_ranking(movies)
#print
#print "From ranking:",len(movies_new)
#for movie in movies_new:
#    print movie