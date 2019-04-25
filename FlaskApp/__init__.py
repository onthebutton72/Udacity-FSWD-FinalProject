from flask import session as login_session
from flask_marshmallow import Marshmallow
from flask import make_response

import requests
import random
import string
import httplib2
import json

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)
APP_PATH = '/var/www/FlaskApp/FlaskApp/'
CLIENT_ID = json.loads(
    open(APP_PATH + 'client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Movie Catalog App"

Base = automap_base()
engine = create_engine('postgresql:///catalog')
Base.prepare(engine, reflect=True)
Genres = Base.classes.genres
Movies = Base.classes.movies
session = Session(engine)
ma = Marshmallow(app)


# Classes for JSON Marshmallow
class GenreSchema(ma.ModelSchema):
    class Meta:
        model = Genres


# Classes for JSON Marshmallow
class MovieSchema(ma.ModelSchema):
    class Meta:
        model = Movies


# Create a route for gconnect function
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(APP_PATH + 'client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Create a route for root webpage
@app.route('/')
# Create a route for mainMenu function
@app.route('/catalog/')
def mainMenu():
    genres = session.query(Genres)
    movies = session.query(Movies).order_by(desc(Movies.id)).limit(3)
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template(
        'catalog.html', genres=genres, movies=movies, STATE=state)


# Create a route for oneGenreJSON function
@app.route('/catalog/<int:genre_id>/JSON/')
def oneGenreJSON(genre_id):
    genres = session.query(Genres).filter_by(id=genre_id).one()
    movies = session.query(Movies).filter_by(genre_id=genre_id).all()
    genre_schema = GenreSchema()
    movie_schema = MovieSchema(many=True)
    output = movie_schema.dump(movies).data
    return jsonify({'Genre_JSON': output})

# Create a route for allMoviesJSON function
@app.route('/catalog/JSON/')
def allMoviesJSON():
    genres = session.query(Genres).all()
    movies = session.query(Movies).all()
    genre_schema = GenreSchema(many=True)
    movie_schema = MovieSchema(many=True)
    output = movie_schema.dump(movies).data
    return jsonify({'All_Movies_JSON': output})


# Create a route for movieMenu function
@app.route('/catalog/movies/<int:genre_id>/')
def movieMenu(genre_id):
    if 'username' not in login_session:
        flash("!!!Please log in to view movies!!!")
        return redirect('/catalog')
    genres = session.query(Genres).filter_by(id=genre_id).one()
    movies = session.query(Movies).filter_by(genre_id=genre_id)
    return render_template(
        'movies.html', genre_id=genre_id, genres=genres, movies=movies)


# Create a route for movieItem function
@app.route('/catalog/movies/item/<int:genre_id>/<int:movie_id>/')
def movieItem(genre_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    genres = session.query(Genres).filter_by(id=genre_id).one()
    movies = session.query(Movies).filter_by(id=movie_id).one()
    return render_template(
        'item.html', genre_id=genre_id, genres=genres, movies=movies)


# Create a route for newMovieItem function
@app.route('/catalog/new/<int:genre_id>/', methods=['GET', 'POST'])
def newMovieItem(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newMovie = Movies(
            title=request.form['title'],
            description=request.form['description'], genre_id=genre_id)
        session.add(newMovie)
        session.commit()
        flash("!!!new movie created!!!")
        return redirect(url_for('movieMenu', genre_id=genre_id))
    else:
        return render_template('newmovieitem.html', genre_id=genre_id)


# Create a route for editMovieItem function
@app.route(
    '/catalog/edit/<int:genre_id>/<int:movie_id>/', methods=['GET', 'POST'])
def editMovieItem(genre_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Movies).filter_by(id=movie_id).one()
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("!!!movie has been edited!!!")
        return redirect(url_for('movieMenu', genre_id=genre_id))
    else:
        return render_template(
            'editmovieitem.html', genre_id=genre_id, movie_id=movie_id,
            i=editedItem)

# Create a route for deleteMovieItem function
@app.route(
    '/catalog/delete/<int:genre_id>/<int:movie_id>/', methods=['GET', 'POST'])
def deleteMovieItem(genre_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Movies).filter_by(id=movie_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("!!!movie has been deleted!!!")
        return redirect(url_for('movieMenu', genre_id=genre_id))
    else:
        return render_template('deletemovieitem.html', i=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'mykey'
    app.debug = True
    app.run()
