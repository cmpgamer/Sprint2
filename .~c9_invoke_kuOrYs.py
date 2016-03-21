import sys
import resource
from recommender import recommender
reload(sys)
sys.setdefaultencoding("UTF8")
import os
import uuid
from flask import *
from flask.ext.socketio import SocketIO, emit
from flask_socketio import join_room, leave_room
import psycopg2
import psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def connect_to_db():
    # return psycopg2.connect('dbname=movie_recommendations user=movieAdmin password=password host=localhost')
    return psycopg2.connect('dbname=movie_recommendations user=postgres password=Cmpgamer1 host=localhost')
    
@socketio.on('connect', namespace='/movie')
def makeConnection():
    session['uuid'] = uuid.uuid1()
    print ('Connected')
    
@socketio.on('identify', namespace='/movie')
def on_identify(user):
    print('Identify: ' + user)
    users[session['uuid']] = {'username' : user}
    
    
movieSearchQuery = "SELECT movie_title FROM movie_titles WHERE movie_title LIKE %s" 
newMovieSearch = "select mt.movie_title,  my.year from movie_titles mt join movie_years my on mt.id = my.movie_id WHERE movie_title LIKE %s"
movieGenreSearch = "select mt.movie_title, mg.movie_genre from movie_titles mt join movie_genres mg on mt.id = mg.movie_id WHERE movie_title LIKE %s"
@socketio.on('search', namespace='/movie')
def search(searchItem):
    

    db = connect_to_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    searchQuery = ""
    results = []
    queryResults = []
    searchTerm = '%{0}%'.format(searchItem)
    
    #print(searchTerm)
    
    try:
        cur.execute(newMovieSearch, (searchTerm,))
        results = cur.fetchall()
    except Exception as e:
        print("Error: Invalid SEARCH in 'movie_titles' table: %s" % e)
    
    try:
        cur.execute(movieGenreSearch, (searchTerm,))
        genreResults = cur.fetchall()
    except Exception as e:
        print("Error: Invalid SEARCH in 'movie_titles' table: %s" % e)
    
    movieGenres = {}
    copyGenres = genreResults
    parsedResults = []
    
    for i in range(len(genreResults)):
        for j in range(len(copyGenres)):
            if genreResults[i][0] == copyGenres[j][0] and i != j:
                genreResults[i][1] += copyGenres[j][1]
                
    
                
            
      
    parsedResults    
    print(genreResults)
    
    
    for i in range(len(results)):
        
        resultsDict = {'text' : results[i]['movie_title'], 'year' : results[i]['year']}
        queryResults.append(resultsDict)
    
    #print(queryResults)
     
    cur.close()
    db.close()
    emit('searchResults', queryResults)
        
doesUserAlreadyExist = 'SELECT * FROM users WHERE username = %s LIMIT 1'
registerNewUser = "INSERT INTO users VALUES (default, %s, %s, %s, crypt(%s, gen_salt('md5')))"
@app.route('/register', methods=['GET', 'POST'])
def register():
    redirectPage = 'landing.html'
    error = ''
    if request.method == 'POST':
        db = connect_to_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        username = request.form['registerUsername']
        password = request.form['registerPassword']
        password2 = request.form['registerConfirmPassword']
        
        if username.isspace():
            error += 'Username is required.\n'
        if firstName.isspace():
            error += 'First Name is required.\n'
        if lastName.isspace():
            error += 'Last Name is required.\n'
        if password.isspace():
            error += 'Password is required.\n'
        if password2.isspace():
            error += 'Password must be entered in twice.\n'
        if password != password2:
            error += 'Passwords do not match.\n'
        
        if len(error) == 0:
            try:
                cur.execute(doesUserAlreadyExist, (username,)) # check whether user already exists
                
                if cur.fetchone():
                    error += 'Username is already taken.\n'
                else:
                    try:
                        cur.execute(registerNewUser, (firstName, lastName, username, password)) # add user to database
                        db.commit()
                    except Exception as e:
                        print("Error: Invalid INSERT in 'user' table: %s" % e)
            except Exception as e:
                print("Error: Invalid SEARCH in 'user' table: %s" % e)

        cur.close()
        db.close()

        if len(error) != 0:
            redirectPage = 'landing.html'
            
    if len(error) != 0:
        pass
        # flash error message
        
    return render_template(redirectPage, error=error)
    
loginQuery = 'SELECT * from users WHERE username = %s AND password = crypt(%s, password)'
@app.route('/login', methods=['GET', 'POST'])
def login():
    redirectPage = 'landing.html'
    error = ''
    results = None
    
    if request.method == 'POST':
        
        db = connect_to_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        username = request.form['username']
        
        pw = request.form['password']

        try:
            cur.execute(loginQuery, (username, pw))
            results = cur.fetchone()
        except Exception as e:
            print("Error: SEARCH in 'user' table: %s" % e)
        
        cur.close()
        db.close()
        
        if not results: # user does not exist
            error += 'Incorrect username or password.\n'
        else:
            print(results['username'])
            session['username'] = results['username']
            session['id'] = results['id']
            results = []
            return redirect(url_for('index'))
         
    if len(error) != 0:
        pass
        # flash error
        
    return render_template(redirectPage, error=error)

@app.route('/landing',  methods=['GET', 'POST'])
def landing():
   
    if 'username' in session:
        print("index")
        db = connect_to_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #get dynamic top 12
        query = "SELECT movie_titles.movie_title, movie_ratings.rating FROM movie_titles INNER JOIN movie_ratings ON movie_titles.id=movie_ratings.movie_id ORDER BY movie_ratings.rating DESC LIMIT 12;"
        #print("are we getting here?????????????")
        try:
            cur.execute(query)
            results=cur.fetchall()
        except Exception, e:
            raise e
        return render_template('index.html', results=results)
    else:
        return render_template('landing.html')


@app.route('/', methods=['GET', 'POST'])
def index():
   
    if 'username' in session:
        print("index")
        db = connect_to_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #get dynamic top 12
        query = "SELECT movie_titles.movie_title, movie_ratings.rating FROM movie_titles INNER JOIN movie_ratings ON movie_titles.id=movie_ratings.movie_id ORDER BY movie_ratings.rating DESC LIMIT 12;"
        #print("are we getting here?????????????")
        try:
            cur.execute(query)
            results=cur.fetchall()
        except Exception, e:
            
            raise e
            
        
        return render_template('index.html', results=results)
    else:
        return render_template('landing.html')    

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))
    
movieRatingQuery = "SELECT mt.movie_title as movie_id, u.id, mr.rating FROM movie_ratings mr JOIN users u on u.id = mr.user_id JOIN movie_titles mt ON mt.id = mr.movie_id"
movieIDQuery = "SELECT * FROM movie_titles"
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    redirectPage = 'recommendations.html'
    data = {}
    productid2name = {}
    userRatings= {}
    db = connect_to_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cur.execute(movieRatingQuery)
        results = cur.fetchall()
    except Exception as e:
        print("Error: SEARCH in 'movie_ratings table: %s" % e)
    
    for row in results:
        user = row['id']
        movie = row['movie_id']
        rating = float(row['rating'])
        if user in data:
            currentRatings = data[user]
        else:
            currentRatings = {}
        currentRatings[movie] = rating
        data[user] = currentRatings
    
    try:
        cur.execute(movieIDQuery)
        results = cur.fetchall()
    except Exception as e:
        print("Error: SEARCH in 'movie_titles' table: %s" % e)
    
    cur.close()
    db.close()
    movieLens = recommender(5, 15) #Manhattan Distance 5 Nearest Neighbors
    movieLens.data = data
    results = movieLens.recommend(session['id'])

    return render_template(redirectPage)

getMovieIDQuery= "SELECT id FROM movie_titles WHERE movie_title= %s "
insertRateQuery= "INSERT INTO movie_ratings VALUES(default,%s,%s,%s)" 

@app.route('/rateMovie', methods=['GET', 'POST'])
def rateMovie():
    redirectPage= "index.html"
    
    print("test1")
    
    db = connect_to_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    #insert movie, insert review
    #movie with person id into movie_rating table
    #person id, movie, rating
    if request.method == 'POST':
        movie_title= request.form['moviename']
        print("test")
        print(movie_title)
        try:
            cur.execute(getMovieIDQuery, (movie_title,))
            results = cur.fetchone()
        except Exception as e:
            print(e)
        # try:
        #     cur.execute(insertRateQuery, (movie_title
        # except Exception as e:
        #    print(e)
        #print(results)
    return render_template(redirectPage)


    
# start the server
if __name__ == '__main__':
        socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port =int(os.getenv('PORT', 8080)), debug=True)
