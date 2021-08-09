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
import datetime
import sys

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

def format_datetime(value):
  date = dateutil.parser.parse(value)
  # if format == 'full':
  #     format="EEEE MMMM, d, y 'at' h:mma"
  # elif format == 'medium':
  #     format="EE MM, dd, y h:mma"
  # return babel.dates.format_datetime(date, format, locale='en')
  return babel.dates.format_datetime(date, 'EEEE, MMMM dd y', locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  venues = Venue.query.all()
  for venue in venues:
    venue_data = {}
    venue_data['id'] = venue.id
    venue_data['name'] = venue.name
    venue_data['release_date'] = venue.release_date
    data.append(venue_data)

  return render_template('pages/venues.html', venues=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.

  search_term = request.form.get('search_term', '')
  venue_query = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  venue_list = []
  for venue in venue_query:
      venue_list.append({
          "id": venue.id,
          "name": venue.name,
          "release_date": venue.release_date
      })

  response = {
      "count": len(venue_list),
      "data": venue_list
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter(Venue.id == venue_id)[0]
  venue_data = {}
  venue_data['id'] = venue.id
  venue_data['name'] = venue.name
  venue_data['release_date'] = venue.release_date

  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    venue_form = form.data
    try:
      venue = Venue(
        name=venue_form['name'],
        release_date=venue_form['release_date']
      )
      db.session.add(venue)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Venue ' + venue_form['name'] + ' could not be listed.')
      return redirect(url_for('create_venue_form'))
    else:
      flash('Venue ' + venue_form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
    return redirect(url_for('create_venue_form'))

@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Delete was unsuccessful. Try again!')
    return redirect(url_for('venues'))
  else:
    flash('The Venue has been successfully deleted!')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
    artist_data = {}
    artist_data['id'] = artist.id
    artist_data['name'] = artist.name
    artist_data['age'] = artist.age
    artist_data['gender'] = artist.gender
    data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.

  search_term = request.form.get('search_term', '')
  artist_query = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))
  artist_list = []
  for artist in artist_query:
    artist_list.append({
      "id": artist.id,
      "name": artist.name,
      "age": artist.age,
      "gender": artist.gender
    })

  response = {
    "count": len(artist_list),
    "data": artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: use Artist.shows instead
  artist = Artist.query.filter(Artist.id == artist_id)[0]
  artist_data = {}
  artist_data['id'] = artist.id
  artist_data['name'] = artist.name
  artist_data['age'] = artist.age
  artist_data['gender'] = artist.gender

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id)[0]
  artist_data={
    "id": artist.id,
    "name": artist.name,
    "age": artist.age,
    "gender": artist.gender
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      artist = Artist.query.get(artist_id)
      artist_form = form.data
      for key in artist_form:
        if artist_form[key] == '': # skip empty fields
          continue
        artist.__setattr__(key, artist_form[key])
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('error committing to database')
      return redirect(url_for('show_artist', artist_id=artist_id))
    else:
      flash('Artist successfully edited')
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
    # https://stackoverflow.com/questions/21294889/how-to-get-access-to-error-message-from-abort-command-when-using-custom-error-ha
    # abort(500, {'message': str(message)})
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id)[0]
  venue_data={
    "id": venue.id,
    "name": venue.name,
    "release_date": venue.release_date,
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      venue_form = form.data
      for key in venue_form:
        if venue_form[key] == '': # skip empty fields
          continue
        venue.__setattr__(key, venue_form[key])
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('error committing to database')
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      flash('Venue successfully edited')
      return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    artist_form = form.data
    try:
      artist = Artist(
        name=artist_form['name'],
        age=artist_form['age'],
        gender=artist_form['gender']
      )
      db.session.add(artist)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist ' + artist_form['name'] + ' could not be listed.')
      return redirect(url_for('create_artist_form'))
    else:
      flash('Artist ' + artist_form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
    return redirect(url_for('create_artist_form'))

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
