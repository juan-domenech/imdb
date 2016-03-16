import MySQLdb as _mysql
import imdb

# For the search&replace of bad characters
import re

DEBUG = 0

ia = imdb.IMDb()

class MySQLDatabase:
    def __init__ (self, database_name, username, password, host='localhost') :
        try:
            self.db = _mysql.connect(db=database_name,
                                     host=host,
                                     user=username,
                                     passwd=password)
            self.database_name=database_name
            if DEBUG == 1:
                print "Connected to MySQL!"
        except _mysql.Error, e:
            print e


    def __del__( self ):
        if hasattr(self, 'db'): # close our connection to free it up in the pool
            self.db.close()
            if DEBUG == 1:
                print "MySQL Connection closed"


    # Check whether this search string is stored in DB
    def check_search(self,search):
        # Compare the search string with all the previous stored searches and return the search_id
        sql = "SELECT search_id FROM searches WHERE search='"+search+"';"
        if DEBUG == 1:
            print sql
        cursor = self.db.cursor()
        cursor.execute(sql)
        search_id = cursor.fetchone()
        if search_id:
            if DEBUG == 1:
                print search_id
            cursor.close()
            return search_id[0]
        else:
            if DEBUG == 1:
                print "Search not found in DB"
            cursor.close()
            return False


    # Free test search in IMDB when the search is not present in the DB
    def get_movies_by_name(self,search):
        ia = imdb.IMDb()
        s_result = ia.search_movie( search )
        if s_result:
            if DEBUG == 1:
                print "s_result:",s_result
                for item in range(0,len(s_result)):
                    print "item:",s_result[item].data
            return s_result
        else:
            if DEBUG == 1:
                print "No movies found!"
            return {}


    # Get from DB all the movies under the same search_id
    def get_movies_by_stored_search(self, search_id):
        movies_clean = []
        sql = "SELECT * FROM movies WHERE search_id='"+str(search_id)+"';"
        if DEBUG == 1:
            print sql
        cursor = self.db.cursor()
        cursor.execute(sql)
        movies = cursor.fetchall()
        if len(movies):
            if DEBUG == 1:
                print "Return from DB"
                for item in range(0,len(movies)):
                    print movies[item]
            for movie in movies:
                movies_clean.append(self.movie_from_tuple_to_dictionary(movie))
            if DEBUG == 1:
                print "movies_clean:",movies_clean
            return movies_clean
        else:
            if DEBUG == 1:
                print "Something went wrong. No movies stored under this search_id:", search_id
            # Delete invalid search ID as workaround
            self.remove_invalid_search_id(search_id)
            return False

    # Remove search_id that has no associated movies
    def remove_invalid_search_id(self,search_id):
        sql = "DELETE FROM searches WHERE search_id='"+str(search_id)+"';"
        if DEBUG == 1:
            print "Removing search_id:", search_id
            print sql
        cursor = self.db.cursor()
        cursor.execute(sql)
        #movies = cursor.fetchall()
        self.db.commit()
        return

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
        if movie[6]:
            result['akas'] = movie[6]
        # Not a IMDB field but we add it anyway
        result['search id'] = int(str(movie[7]))
        return result


    #
    def insert_search(self, search):
        sql = "INSERT INTO searches (search) VALUES ('"+str(search)+"');"
        if DEBUG == 1:
            print sql
        cursor = self.db.cursor()
        cursor.execute(sql)

        # Let's do commit as a last step instead
        #self.db.commit()

        # Recover search_id from the last Insert
        return self.check_search(search)


    # Create simplified object with only the properties we are interested on
    def normalize_imdb_response(self, s_result):
        movies = []
        for item in s_result:
            movie = {}
            movie['movieID'] = int(item.movieID)
            movie['year'] = 2155
            if DEBUG == 1:
                print "item.data:",item.data
            for item_data in item.data:
                # Add new property&value to the object that are present in .data object
                movie[item_data] = item.data[item_data]
                if DEBUG == 1:
                    print "item_data:",item_data, "item.data[item_data]:",item.data[item_data]

            # Deal with the akas field format issue: Store only the first one
            if movie.has_key('akas'):
                movie['akas'] = movie['akas'][0]

            # Replace single quotes
            movie['title'] = re.sub("'", "\\'", movie['title'] )
            if movie.has_key('episode of'):
                movie['episode of'] = re.sub("'", "\\'", movie['episode of'] )
            if movie.has_key('akas'):
                movie['akas'] = re.sub("'", "\\'", movie['akas'] )

            movies.append(movie)
        return movies


    # Insert movies into DB
    def insert_movies_into_db(self, search_id, movies):

        for movie in movies:

            # Using IGNORE to avoid duplicates (To Improve)
            #sql = "INSERT IGNORE INTO movies (`search_id`,"
            # Let's try using REPLACE
            sql = "REPLACE INTO movies (`search_id`,"
            sql_values = "VALUES ('"+str(search_id)+"',"

            for item in movie:
                if DEBUG == 1:
                    print "item:",item

                sql += "`"+str(item)+"`,"
                sql_values += "'"+str(movie[item])+"',"
                #sql_values += "'"+movie[item]+"',"

            sql = sql[:-1]+") "+(sql_values[:-1])+");"

            if DEBUG == 1:
                print sql
            cursor = self.db.cursor()
            cursor.execute(sql)
        self.db.commit()
        return


    # Search for similar movies in DB using LIKE and add to the final list
    def get_movies_by_like(self, search, movies = [] ):
        movies_clean = []
        sql = "SELECT * FROM movies WHERE title LIKE '%"+search+"%';"
        if DEBUG == 1:
            print sql
        cursor = self.db.cursor()
        cursor.execute(sql)
        movies_from_db = cursor.fetchall()
        if len(movies_from_db):
            if DEBUG == 1:
                print "Return from DB:", len(movies_from_db)
                for item in range(0,len(movies_from_db)):
                    print movies_from_db[item]
            # Convert tuples to IMDB format
            for movie in movies_from_db:
                movies_clean.append(self.movie_from_tuple_to_dictionary(movie))

            if DEBUG == 1:
                if movies:
                    print "What we have from search_id:",len(movies)
                    for movie in sorted(movies):
                        print movie
                else:
                    print "ERROR: No movies from search:",search
                print "What we have from LIKE search:",len(movies_clean)
                for movie in sorted(movies_clean):
                    print movie

            # Add to movies the new additions from movie_clean
            movies_new = []
            for movie_clean in movies_clean:
                if movie_clean not in movies:
                    if DEBUG == 1:
                        print "Match found", movie_clean
                    movies_new.append(movie_clean)
            movies = movies + movies_new

            if DEBUG == 1:
                print "What we have combined:",len(movies)
                for movie in sorted(movies):
                    print movie

            return movies

        # Nothing to add from DB. Return what we already have.
        return movies



    #
    # Main "search by string" function
    #
    def search(self,search):

        # Check whether this search already exists
        search_id = self.check_search(search)

        # The movie search exits in DB -> get the list of associated movies + return them
        if search_id:
            if DEBUG == 1:
                print "Search '"+search+"' found id DB with search_ID:",search_id
            movies = self.get_movies_by_stored_search(search_id)

            # Search for similar movies in DB using LIKE and add to the final list
            movies = self.get_movies_by_like(search)

            if movies:
                if DEBUG == 1:
                    print sorted(movies)
                return movies
            else:
                if DEBUG == 0 or DEBUG == 1:
                    print "ERROR: Something went wrong. No movies from a present search_id:", search_id
                # Exit with empty due error
                return []

        # The movie search doesn't exist in the DB -> Search IMDB + update DB + search by LIKE in DB + return them
        else:
            if DEBUG == 1:
                print "Search '"+search+"' not found. Connecting to IMDB..."

            # Send search to IMDB
            s_result = self.get_movies_by_name(search)

            # No results -> break
            if len(s_result) == 0:
                if DEBUG == 0 or DEBUG == 1:
                    print "No movies found in IMDB, weird..."
                return []

            # Normalize response from IMDB API
            movies = self.normalize_imdb_response(s_result)

            # Store search string and get search_id
            search_id = self.insert_search(search)
            if search_id:
                if DEBUG == 1:
                    print "New search_id: %i for Search: %s" % ( search_id, search)
            else:
                if DEBUG == 0 or DEBUG == 1:
                    print "ERROR: Something went wrong: No search_id returned after INSERT"
                # Exit with empty due error
                return []

            # Insert Movies into DB and commit
            self.insert_movies_into_db(search_id, movies)

            if len(movies) == 0:
                if DEBUG == 0 or DEBUG == 1:
                    print "ERROR: movies len == 0 weird..."
                return []

            # Search for similar movies in DB using LIKE and add to the final list
            movies = self.get_movies_by_like(search,movies)

            if DEBUG == 1:
                for item in movies:
                    print item

            return movies


