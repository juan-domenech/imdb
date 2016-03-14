DEBUG = True

import MySQLdb as _mysql
import imdb

ia = imdb.IMDb()

class MySQLDatabase:
    def __init__ (self, database_name, username, password, host='localhost') :
        try:
            self.db = _mysql.connect(db=database_name,
                                     host=host,
                                     user=username,
                                     passwd=password)
            self.database_name=database_name
            if DEBUG:
                print "Connected to MySQL!"
        except _mysql.Error, e:
            print e


    def __del__( self ):
        if hasattr(self, 'db'): # close our connection to free it up in the pool
            self.db.close()
            if DEBUG:
                print "MySQLConnectionclosed"


    # Check whether this search string has already been used
    def check_search(self,search):
        # Compare the search string with all the previous stored searches and return the search_id
        sql = "SELECT search_id FROM searches WHERE search='"+search+"';"
        if DEBUG:
            print sql
        cursor = self.db.cursor()
        cursor.execute(sql)
        search_id = cursor.fetchone()
        if search_id:
            if DEBUG:
                print search_id
            cursor.close()
            return search_id[0]
        else:
            if DEBUG:
                print "Search not found in DB"
            cursor.close()
            return False


    # Free test search in IMDB
    def get_movies_by_name(self,search):
        ia = imdb.IMDb()
        s_result = ia.search_movie( search )
        if s_result:
            if DEBUG:
                print s_result
            return s_result
        else:
            if DEBUG:
                print "No movies found!"
            return False


    # Get from DB all the movies under the same search_id
    def get_movies_by_stored_search(self, search_id):
        movies_clean = []
        sql = "SELECT * FROM movies WHERE search_id='"+str(search_id)+"';"
        if DEBUG:
            print sql
        cursor = self.db.cursor()
        cursor.execute(sql)
        movies = cursor.fetchall()
        if len(movies):
            if DEBUG:
                print "Return from DB"
                for item in range(0,len(movies)):
                    print movies[item]
            for movie in movies:
                movies_clean.append(self.movie_from_tuple_to_dictionary(movie))
            if DEBUG:
                print "movies_clean:",movies_clean
            return movies_clean

        else:
            if DEBUG:
                print "Something went wrong. No movies stored under this search_id:", search_id
            return False


    # Convert a tupple containing the movie information to an object following IMDB module format
    def movie_from_tuple_to_dictionary(self, movie):

        result = {}

        result['movieID'] = int(str(movie[0]))
        result['title'] = movie[1]
        result['year'] = movie[2]
        if movie[3]:
            result['kind'] = movie[3]
        if movie[4]:
            result['episode of'] = movie[4]
        if movie[5]:
            result['series year'] = movie[5]
        # Not a IMDB field but we pass it anyway
        result['search id'] = int(str(movie[6]))

        return result






    # Main search by string function
    def search(self,search):
        # Check whether this search already exists
        search_id = self.check_search(search)

        # The movie search exits in DB
        if search_id:
            if DEBUG:
                print "Search",search,"found id DB with search_ID:",search_id

            movies = self.get_movies_by_stored_search(search_id)
            if movies:
                if DEBUG:
                    print movies
                return movies




            else:
                if DEBUG:
                    print "Something went wrong. No movies from a present search_id:", search_id
            return False


        # The movie search doesn't exists
        else:
            if DEBUG:
                print "Search",search,"not found. Connecting to IMDB..."
            # Send search to IMDB
            s_result = self.get_movies_by_name(search)
            if DEBUG:
                for item in s_result:
                    print item.data


            return


