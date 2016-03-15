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
    
@socketio.on('rate', namespace='/movie')
def rate(result):
    resultList = []
    resultList.append(result)
    emit('rateResults', resultList)
    
    
movieSearchQuery = "SELECT movie_title FROM movie_titles WHERE movie_title LIKE %s"    
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
        cur.execute(movieSearchQuery, (searchTerm,))
        results = cur.fetchall()
    except Exception as e:
        print("Error: Invalid SEARCH in 'movie_titles' table: %s" % e)
    
    for i in range(len(results)):
        resultsDict = {'text' : results[i]['movie_title']}
        queryResults.append(resultsDict)
    
    #print(queryResults)
     
    cur.close()
    db.close()
    emit('searchResults', queryResults)
        
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return render_template('landing.html')    
    
    
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
    print("I got here")
    if request.method == 'POST':
        
        db = connect_to_db()
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        username = request.form['username']
        print(username)
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

@app.route('/landing')
def landing():
    if 'username' in session:
        return render_template('index.html')
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
    
    # for row in results:
    #     movieID = row['id']
    #     title = row['movie_title']
    #     productid2name[movieID] = title
    
    cur.close()
    db.close()
    
    movieLens = recommender(5, 15) #Manhattan Distance 5 Nearest Neighbors
    movieLens.data = data
    
    results = movieLens.recommend(session['id'])

    return render_template(redirectPage)


    
# start the server
if __name__ == '__main__':
        socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port =int(os.getenv('PORT', 8080)), debug=True)
