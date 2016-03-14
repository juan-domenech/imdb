from database.mysql import MySQLDatabase

db = MySQLDatabase('imdb','imdb','imdb','localhost')


movies = db.search('test')
print "Main"
for movie in movies:
    print movie

