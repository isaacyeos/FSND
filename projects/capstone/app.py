from flask import (
    Flask,
    request,
    jsonify,
    abort
)
import sys
from auth.auth import requires_auth
from models import setup_db, Movie, Actor, db, db_drop_and_create_all
from sqlalchemy import exc
from flask_cors import CORS
import os

def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)

  if "LOCAL_APP" in os.environ:
    db_drop_and_create_all()

  CORS(app, resources={r"/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/')
  def index():
    return jsonify({'success': True}), 200

  @app.route('/movies', methods=['GET'])
  @requires_auth('get:movies')
  def get_movies():
    data = []
    movies = Movie.query.all()
    for movie in movies:
      movie_data = {}
      movie_data['id'] = movie.id
      movie_data['title'] = movie.title
      movie_data['release_date'] = movie.release_date
      data.append(movie_data)

    return jsonify({"success": True,
                    "movies": [movie['title'] for movie in data]}), 200

  @app.route('/movies/<int:movie_id>', methods=['GET'])
  @requires_auth('get:movies')
  def get_movie_by_id(movie_id):
    movie = Movie.query.get(movie_id)
    if movie is None:
      abort(404, 'no such movie exists')
    movie_data = {}
    movie_data['id'] = movie.id
    movie_data['title'] = movie.title
    movie_data['release_date'] = movie.release_date
    movie_data['actors'] = movie.actors
    movie_data['image_link'] = movie.image_link

    return jsonify({"success": True,
                    "movie_id": movie_data['id'],
                    "movie": movie_data['title'],
                    "actors": [actor.name for actor in movie_data['actors']]}), 200

  @app.route('/movies', methods=['POST'])
  @requires_auth('post:movies')
  def create_movie():
    try:
      movie_data = request.get_json()
      movie = Movie(
        title=movie_data['title'],
        release_date=movie_data['release_date'],
        image_link=movie_data['image_link']
      )
      actor_names = movie_data['actors']
      actors = Actor.query.filter(Actor.name.in_(actor_names))
      for actor in actors:
        movie.actors.append(actor)
      db.session.add(movie)
      db.session.commit()

      return jsonify({"success": True,
                      "movie_id": movie.id,
                      "movie": movie.title,
                      "actors": [actor.name for actor in movie.actors]}), 200
    except Exception as e:
      print(sys.exc_info())
      if type(e) is KeyError or type(e) is exc.IntegrityError:
        abort(422, 'invalid json parameters')
      else:
        abort(500)

  @app.route('/movies/<int:movie_id>', methods=['PATCH'])
  @requires_auth('patch:movies')
  def update_movie(movie_id):
    try:
      movie_data = request.get_json()
      movie = Movie.query.get(movie_id)
      movie.title = movie_data['title']
      movie.release_date = movie_data['release_date']
      movie.image_link = movie_data['image_link']
      actor_names = movie_data['actors']
      current_actor_names = [actor.name for actor in movie.actors]
      actor_names_new = list(filter(lambda actor_name: actor_name not in current_actor_names, actor_names))
      actors = Actor.query.filter(Actor.name.in_(actor_names_new))
      for actor in actors:
        movie.actors.append(actor)
      for actor in movie.actors:
        if actor.name not in actor_names:
          movie.actors.remove(actor)
      db.session.commit()

      return jsonify({"success": True,
                      "movie_id": movie.id,
                      "movie": movie.title,
                      "actors": [actor.name for actor in movie.actors]}), 200

    except (KeyError, exc.IntegrityError):
      print(sys.exc_info())
      abort(422, 'invalid json parameters')
    except Exception:
      print(sys.exc_info())
      abort(500)

  @app.route('/movies/<int:movie_id>', methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if movie is None:
      abort(404, 'no such movie exists')
    try:
      db.session.delete(movie)
      db.session.commit()
      return jsonify({
        "success": True,
        "movie_id": movie.id,
        "movie": movie.title
      }), 200
    except:
      print(sys.exc_info())
      abort(500)

  #  Actors
  #  ----------------------------------------------------------------
  @app.route('/actors', methods=['GET'])
  @requires_auth('get:actors')
  def actors():
    data = []
    actors = Actor.query.all()
    for actor in actors:
      actor_data = {}
      actor_data['id'] = actor.id
      actor_data['name'] = actor.name
      actor_data['age'] = actor.age
      actor_data['gender'] = actor.gender
      data.append(actor_data)

    return jsonify({
      "success": True,
      "actors": [actor['name'] for actor in data]
    }), 200

  @app.route('/actors/<int:actor_id>', methods=['GET'])
  @requires_auth('get:actors')
  def get_actor_by_id(actor_id):
    actor = Actor.query.get(actor_id)
    if actor is None:
      abort(404, 'no such actor exists')
    actor_data = {}
    actor_data['id'] = actor.id
    actor_data['name'] = actor.name
    actor_data['age'] = actor.age
    actor_data['gender'] = actor.gender
    actor_data['movies'] = actor.movies
    actor_data['image_link'] = actor.image_link

    return jsonify({
      "success": True,
      "actor_id": actor_data['id'],
      "actor": actor_data['name'],
      "movies": [movie.title for movie in actor_data['movies']]
    }), 200

  @app.route('/actors', methods=['POST'])
  @requires_auth('post:actors')
  def create_actor():
    try:
      actor_data = request.get_json()
      actor = Actor(
        name=actor_data['name'],
        age=actor_data['age'],
        gender=actor_data['gender'],
        image_link=actor_data['image_link']
      )
      movie_titles = actor_data['movies']
      movies = Movie.query.filter(Movie.title.in_(movie_titles))
      for movie in movies:
        actor.movies.append(movie)

      db.session.add(actor)
      db.session.commit()

      return jsonify({
        "success": True,
        "actor_id": actor.id,
        "actor": actor.name,
        "movies": [movie.title for movie in actor.movies]
      }), 200

    except (KeyError, exc.IntegrityError):
      print(sys.exc_info())
      abort(422, 'invalid json parameters')
    except Exception:
      print(sys.exc_info())
      abort(500)

  @app.route('/actors/<int:actor_id>', methods=['PATCH'])
  @requires_auth('patch:actors')
  def update_actor(actor_id):
    try:
      actor_data = request.get_json()
      actor = Actor.query.get(actor_id)
      actor.name = actor_data['name']
      actor.age = actor_data['age']
      actor.gender = actor_data['gender']
      actor.image_link = actor_data['image_link']
      movie_titles = actor_data['movies']
      current_movie_titles = [movie.title for movie in actor.movies]
      movie_titles_new = list(filter(lambda movie_title: movie_title not in current_movie_titles, movie_titles))
      movies = Movie.query.filter(Movie.title.in_(movie_titles_new))
      for movie in movies:
        actor.movies.append(movie)
      for movie in actor.movies:
        if movie.title not in movie_titles:
          actor.movies.remove(movie)
      db.session.commit()

      return jsonify({
        "success": True,
        "actor_id": actor.id,
        "actor": actor.name,
        "movies": [movie.title for movie in actor.movies]
      }), 200
    except (KeyError, exc.IntegrityError):
      print(sys.exc_info())
      abort(422, 'invalid json parameters')
    except Exception:
      print(sys.exc_info())
      abort(500)

  @app.route('/actors/<int:actor_id>', methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actor(actor_id):
    actor = Actor.query.get(actor_id)
    if actor is None:
      abort(404, 'no such actor exists')
    try:
      db.session.delete(actor)
      db.session.commit()
      return jsonify({
        "success": True,
        "actor_id": actor.id,
        "actor": actor.name
      }), 200
    except:
      print(sys.exc_info())
      abort(500)

  @app.errorhandler(400)
  @app.errorhandler(401)
  @app.errorhandler(403)
  @app.errorhandler(404)
  @app.errorhandler(405)
  @app.errorhandler(422)
  @app.errorhandler(500)
  def error_handler(error):
    return jsonify({
      'success': False,
      'error': error.code,
      'message': error.description
    }), error.code

  return app

app = create_app()
