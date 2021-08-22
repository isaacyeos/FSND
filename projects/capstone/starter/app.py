#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
import sys
import seeds
from sqlalchemy import exc

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
db = SQLAlchemy(app)

migrate = Migrate(app, db)

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(date):
  return babel.dates.format_datetime(date, 'EEEE, MMMM dd y', locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  if Actor.query.count() == 0 and Movie.query.count() == 0:
    movies = []
    for movie in seeds.movies:
      movieObject = Movie(title=movie['title'],
                          release_date=movie['release_date'],
                          image_link=movie['image_link'])
      movies.append(movieObject)

    actors = []
    for actor in seeds.actors:
      actorObject = Actor(name=actor['name'],
                          age=actor['age'],
                          gender=actor['gender'],
                          image_link=actor['image_link'])
      actors.append(actorObject)

    actors[1].movies = movies
    for movie in movies:
      movie.actors = actors

    for actor in actors:
      try:
        db.session.add(actor)
        db.session.commit()
      except exc.SQLAlchemyError as e:
        print(str(e.__dict__['orig']))
        db.session.rollback()
        print("ERROR committing to database!")
      finally:
        db.session.close()

    for movie in movies:
      try:
        db.session.add(movie)
        db.session.commit()
      except exc.SQLAlchemyError as e:
        print(str(e.__dict__['orig']))
        db.session.rollback()
        print("ERROR committing to database!")
      finally:
        db.session.close()
  return render_template('pages/home.html')


#  Movies
#  ----------------------------------------------------------------

@app.route('/movies')
def movies():
  data = []
  movies = Movie.query.all()
  for movie in movies:
    movie_data = {}
    movie_data['id'] = movie.id
    movie_data['title'] = movie.title
    movie_data['release_date'] = movie.release_date
    data.append(movie_data)

  return render_template('pages/movies.html', movies=data)

@app.route('/movies/search', methods=['POST'])
def search_movies():
  # implement search on actors with partial string search. Ensure it is case-insensitive.

  search_term = request.form.get('search_term', '')
  movie_query = Movie.query.filter(Movie.title.ilike('%' + search_term + '%'))
  movie_list = []
  for movie in movie_query:
      movie_list.append({
          "id": movie.id,
          "title": movie.title,
          "release_date": movie.release_date
      })

  response = {
      "count": len(movie_list),
      "data": movie_list
  }
  return render_template('pages/search_movies.html', results=response, search_term=search_term)

@app.route('/movies/<int:movie_id>')
def show_movie(movie_id):
  # shows the movie page with the given movie_id
  movie = Movie.query.filter(Movie.id == movie_id)[0]
  movie_data = {}
  movie_data['id'] = movie.id
  movie_data['title'] = movie.title
  movie_data['release_date'] = movie.release_date
  movie_data['actors'] = movie.actors
  movie_data['image_link'] = movie.image_link

  return render_template('pages/show_movie.html', movie=movie_data)

#  Create Movie
#  ----------------------------------------------------------------

@app.route('/movies/create', methods=['GET'])
def create_movie_form():
  form = MovieForm()
  return render_template('forms/new_movie.html', form=form)

@app.route('/movies/create', methods=['POST'])
def create_movie_submission():
  error = False
  form = MovieForm(request.form, meta={'csrf': False})
  if form.validate():
    movie_form = form.data
    try:
      movie = Movie(
        title=movie_form['title'],
        release_date=movie_form['release_date'],
        image_link=movie_form['image_link']
      )
      db.session.add(movie)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Movie ' + movie_form['title'] + ' could not be listed.')
      return redirect(url_for('create_movie_form'))
    else:
      flash('Movie ' + movie_form['title'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
    return redirect(url_for('create_movie_form'))

@app.route('/movies/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
  error = False
  try:
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Delete was unsuccessful. Try again!')
    return redirect(url_for('movies'))
  else:
    flash('The Movie has been successfully deleted!')
    return render_template('pages/home.html')

@app.route('/movies/add/<int:actor_id>', methods=['GET'])
def add_movie_form(actor_id):
  actor = Actor.query.get(actor_id)
  movie_ids = [movie.id for movie in actor.movies]
  movies = Movie.query.filter(~Movie.id.in_(movie_ids))
  return render_template('forms/add_movie.html', movies=movies, actor_id=actor_id)

@app.route('/movies/add/<int:actor_id>', methods=['POST'])
def add_movie_submission(actor_id):
  error = False
  movie_titles = request.form.getlist('movies')
  try:
    actor = Actor.query.get(actor_id)
    movies = Movie.query.filter(Movie.title.in_(movie_titles))
    for movie in movies:
      actor.movies.append(movie)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('error committing to database')
    return redirect(url_for('show_actor', actor_id=actor_id))
  else:
    flash('Movie successfully added')
    return redirect(url_for('show_actor', actor_id=actor_id))

@app.route('/movies/<int:movie_id>/<int:actor_id>', methods=['POST'])
def delete_movie_actor(actor_id, movie_id):
  error = False
  try:
    movie = Movie.query.get(movie_id)
    for actor in movie.actors:
      if actor.id == actor_id:
        movie.actors.remove(actor)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('error committing to database')
    return redirect(url_for('show_movie', movie_id=movie_id))
  else:
    flash('Actor successfully deleted')
    return redirect(url_for('show_movie', movie_id=movie_id))

#  Actors
#  ----------------------------------------------------------------
@app.route('/actors')
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

  return render_template('pages/actors.html', actors=data)

@app.route('/actors/search', methods=['POST'])
def search_actors():
  # implement search on actors with partial string search. Ensure it is case-insensitive.

  search_term = request.form.get('search_term', '')
  actor_query = Actor.query.filter(Actor.name.ilike('%' + search_term + '%'))
  actor_list = []
  for actor in actor_query:
    actor_list.append({
      "id": actor.id,
      "name": actor.name,
      "age": actor.age,
      "gender": actor.gender
    })

  response = {
    "count": len(actor_list),
    "data": actor_list
  }

  return render_template('pages/search_actors.html', results=response, search_term=search_term)

@app.route('/actors/<int:actor_id>')
def show_actor(actor_id):
  # shows the actor page with the given actor_id
  # TODO: use Actor.shows instead
  actor = Actor.query.filter(Actor.id == actor_id)[0]
  actor_data = {}
  actor_data['id'] = actor.id
  actor_data['name'] = actor.name
  actor_data['age'] = actor.age
  actor_data['gender'] = actor.gender
  actor_data['movies'] = actor.movies
  actor_data['image_link'] = actor.image_link

  return render_template('pages/show_actor.html', actor=actor_data)

@app.route('/actors/<int:actor_id>', methods=['POST'])
def delete_actor(actor_id):
  error = False
  try:
    actor = Actor.query.get(actor_id)
    db.session.delete(actor)
    db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Delete was unsuccessful. Try again!')
    return redirect(url_for('actors'))
  else:
    flash('The Actor has been successfully deleted!')
    return render_template('pages/home.html')

@app.route('/actors/<int:actor_id>/<int:movie_id>', methods=['POST'])
def delete_actor_movie(actor_id, movie_id):
  error = False
  try:
    actor = Actor.query.get(actor_id)
    for movie in actor.movies:
      if movie.id == movie_id:
        actor.movies.remove(movie)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('error committing to database')
    return redirect(url_for('show_actor', actor_id=actor_id))
  else:
    flash('Movie successfully deleted')
    return redirect(url_for('show_actor', actor_id=actor_id))

#  Update
#  ----------------------------------------------------------------
@app.route('/actors/<int:actor_id>/edit', methods=['GET'])
def edit_actor(actor_id):
  form = ActorForm()
  actor = Actor.query.filter(Actor.id == actor_id)[0]
  actor_data={
    "id": actor.id,
    "name": actor.name,
    "age": actor.age,
    "gender": actor.gender,
    "image_link": actor.image_link
  }
  # TODO: populate form with fields from actor with ID <actor_id>
  return render_template('forms/edit_actor.html', form=form, actor=actor_data)

@app.route('/actors/<int:actor_id>/edit', methods=['POST'])
def edit_actor_submission(actor_id):
  # actor record with ID <actor_id> using the new attributes
  error = False
  form = ActorForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      actor = Actor.query.get(actor_id)
      actor_form = form.data
      for key in actor_form:
        if actor_form[key] == '': # skip empty fields
          continue
        actor.__setattr__(key, actor_form[key])
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('error committing to database')
      return redirect(url_for('show_actor', actor_id=actor_id))
    else:
      flash('Actor successfully edited')
      return redirect(url_for('show_actor', actor_id=actor_id))
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
    # https://stackoverflow.com/questions/21294889/how-to-get-access-to-error-message-from-abort-command-when-using-custom-error-ha
    # abort(500, {'message': str(message)})
    return redirect(url_for('show_actor', actor_id=actor_id))

@app.route('/actors/add/<int:movie_id>', methods=['GET'])
def add_actor_form(movie_id):
  movie = Movie.query.get(movie_id)
  actor_ids = [actor.id for actor in movie.actors]
  actors = Actor.query.filter(~Actor.id.in_(actor_ids))
  return render_template('forms/add_actor.html', actors=actors, movie_id=movie_id)

@app.route('/actors/add/<int:movie_id>', methods=['POST'])
def add_actor_submission(movie_id):
  error = False
  actor_names = request.form.getlist('actors')
  try:
    movie = Movie.query.get(movie_id)
    actors = Actor.query.filter(Actor.name.in_(actor_names))
    for actor in actors:
      movie.actors.append(actor)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('error committing to database')
    return redirect(url_for('show_movie', movie_id=movie_id))
  else:
    flash('Actor successfully added')
    return redirect(url_for('show_movie', movie_id=movie_id))

@app.route('/movies/<int:movie_id>/edit', methods=['GET'])
def edit_movie(movie_id):
  form = MovieForm()
  movie = Movie.query.filter(Movie.id == movie_id)[0]
  movie_data={
    "id": movie.id,
    "title": movie.title,
    "release_date": movie.release_date,
    "image_link": movie.image_link
  }
  # TODO: populate form with values from movie with ID <movie_id>
  return render_template('forms/edit_movie.html', form=form, movie=movie_data)

@app.route('/movies/<int:movie_id>/edit', methods=['POST'])
def edit_movie_submission(movie_id):
  # movie record with ID <movie_id> using the new attributes
  error = False
  form = MovieForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      movie = Movie.query.get(movie_id)
      movie_form = form.data
      for key in movie_form:
        if movie_form[key] == '': # skip empty fields
          continue
        movie.__setattr__(key, movie_form[key])
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('error committing to database')
      return redirect(url_for('show_movie', movie_id=movie_id))
    else:
      flash('Movie successfully edited')
      return redirect(url_for('show_movie', movie_id=movie_id))
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
  return redirect(url_for('show_movie', movie_id=movie_id))

#  Create Actor
#  ----------------------------------------------------------------

@app.route('/actors/create', methods=['GET'])
def create_actor_form():
  form = ActorForm()
  return render_template('forms/new_actor.html', form=form)

@app.route('/actors/create', methods=['POST'])
def create_actor_submission():
  # called upon submitting the new actor listing form
  error = False
  form = ActorForm(request.form, meta={'csrf': False})
  if form.validate():
    actor_form = form.data
    try:
      actor = Actor(
        name=actor_form['name'],
        age=actor_form['age'],
        gender=actor_form['gender'],
        image_link=actor_form['image_link']
      )
      db.session.add(actor)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Actor ' + actor_form['name'] + ' could not be listed.')
      return redirect(url_for('create_actor_form'))
    else:
      flash('Actor ' + actor_form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
    return redirect(url_for('create_actor_form'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
