from database.mysql import MySQLDatabase

db = MySQLDatabase('imdb','imdb','imdb','localhost')


movies = db.search('kill bill vol')

print "Main:"
print len(movies)
for movie in sorted(movies):
    print movie

