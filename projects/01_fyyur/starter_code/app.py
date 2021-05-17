#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yeo@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  unique_city_states = Venue.query.distinct(Venue.city, Venue.state).all()
  for city_state in unique_city_states:
    city_state_data = {}
    city_state_data['city'] = city_state.city
    city_state_data['state'] = city_state.state
    city_state_data['venues'] = []
    venues = Venue.query.filter(Venue.city == city_state.city)
    for venue in venues:
      venue_data = {}
      venue_data['id'] = venue.id
      venue_data['name'] = venue.name
      shows = Show.query.filter(Show.venue_id == venue.id)
      upcoming_shows = shows.filter(Show.start_time > datetime.datetime.now())
      num_upcoming_shows = upcoming_shows.count()
      venue_data['num_upcoming_shows'] = num_upcoming_shows
      city_state_data['venues'].append(venue_data)
    data.append(city_state_data)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  
  search_term = request.form.get('search_term', '')
  venue_query = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  venue_list = []
  for venue in venue_query:
      venue_list.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.datetime.now()).count()
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
  venue_data['genres'] = json.loads(venue.genres)
  venue_data['address'] = venue.address
  venue_data['city'] = venue.city
  venue_data['state'] = venue.state
  venue_data['phone'] = venue.phone
  venue_data['website'] = venue.website
  venue_data['facebook_link'] = venue.facebook_link
  venue_data['seeking_talent'] = venue.seeking_talent
  if venue.seeking_description != None:
    venue_data['seeking_description'] = venue.seeking_description
  venue_data['image_link'] = venue.image_link
  shows = Show.query.filter(Show.venue_id == venue.id)
  upcoming_shows = shows.filter(Show.start_time > datetime.datetime.now())
  past_shows = shows.filter(Show.start_time <= datetime.datetime.now())
  upcoming_shows_count = upcoming_shows.count()
  past_shows_count = past_shows.count()
  venue_data['past_shows_count'] = past_shows_count
  venue_data['upcoming_shows_count'] = upcoming_shows_count

  venue_data['past_shows'] = []
  for show in past_shows:
    show_data = {}
    show_data['artist_id'] = show.artist_id
    show_data['artist_name'] = Artist.query.filter(Artist.id == show.artist_id)[0].name
    show_data['artist_image_link'] = Artist.query.filter(Artist.id == show.artist_id)[0].image_link
    show_data['start_time'] = show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    venue_data['past_shows'].append(show_data)

  venue_data['upcoming_shows'] = []
  for show in upcoming_shows:
    show_data = {}
    show_data['artist_id'] = show.artist_id
    show_data['artist_name'] = Artist.query.filter(Artist.id == show.artist_id)[0].name
    show_data['artist_image_link'] = Artist.query.filter(Artist.id == show.artist_id)[0].image_link
    show_data['start_time'] = show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    venue_data['upcoming_shows'].append(show_data)

  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

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
    data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.

  search_term = request.form.get('search_term', '')
  artist_query = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))
  artist_list = []
  for artist in artist_query:
    artist_list.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id == artist.id,
                                              Show.start_time > datetime.datetime.now()).count()
    })

  response = {
    "count": len(artist_list),
    "data": artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.filter(Artist.id == artist_id)[0]
  artist_data = {}
  artist_data['id'] = artist.id
  artist_data['name'] = artist.name
  artist_data['genres'] = json.loads(artist.genres)
  artist_data['city'] = artist.city
  artist_data['state'] = artist.state
  artist_data['phone'] = artist.phone
  if artist.website != None:
    artist_data['website'] = artist.website
  artist_data['facebook_link'] = artist.facebook_link
  artist_data['seeking_venue'] = artist.seeking_venue
  if artist.seeking_description != None:
    artist_data['seeking_description'] = artist.seeking_description
  artist_data['image_link'] = artist.image_link
  shows = Show.query.filter(Show.artist_id == artist.id)
  upcoming_shows = shows.filter(Show.start_time > datetime.datetime.now())
  past_shows = shows.filter(Show.start_time <= datetime.datetime.now())
  upcoming_shows_count = upcoming_shows.count()
  past_shows_count = past_shows.count()
  artist_data['past_shows_count'] = past_shows_count
  artist_data['upcoming_shows_count'] = upcoming_shows_count

  artist_data['past_shows'] = []
  for show in past_shows:
    show_data = {}
    show_data['venue_id'] = show.venue_id
    show_data['venue_name'] = Venue.query.filter(Venue.id == show.venue_id)[0].name
    show_data['venue_image_link'] = Venue.query.filter(Venue.id == show.venue_id)[0].image_link
    show_data['start_time'] = show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    artist_data['past_shows'].append(show_data)

  artist_data['upcoming_shows'] = []
  for show in upcoming_shows:
    show_data = {}
    show_data['venue_id'] = show.venue_id
    show_data['venue_name'] = Venue.query.filter(Venue.id == show.venue_id)[0].name
    show_data['venue_image_link'] = Venue.query.filter(Venue.id == show.venue_id)[0].image_link
    show_data['start_time'] = show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    artist_data['upcoming_shows'].append(show_data)

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  shows = Show.query.all()
  for show in shows:
    show_data = {}
    show_data['venue_id'] = show.venue_id
    show_data['venue_name'] = Venue.query.filter(Venue.id == show.venue_id)[0].name
    show_data['artist_id'] = show.artist_id
    show_data['artist_name'] = Artist.query.filter(Artist.id == show.artist_id)[0].name
    show_data['artist_image_link'] = Artist.query.filter(Artist.id == show.artist_id)[0].image_link
    show_data['start_time'] = show.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    data.append(show_data)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
