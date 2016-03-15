from database.mysql import MySQLDatabase

db = MySQLDatabase('imdb','imdb','imdb','localhost')


movies = db.search('Leyla and Mecnun')

print "Main:"
for movie in movies:
    print movie

