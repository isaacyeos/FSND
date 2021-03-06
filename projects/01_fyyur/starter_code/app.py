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
      upcoming_shows = list(filter(lambda show: show.start_time > datetime.datetime.now(), venue.shows))
      num_upcoming_shows = len(upcoming_shows)
      venue_data['num_upcoming_shows'] = num_upcoming_shows
      city_state_data['venues'].append(venue_data)
    data.append(city_state_data)

  return render_template('pages/venues.html', areas=data)

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
          "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.datetime.now(), venue.shows)))
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
  venue_data['genres'] = venue.genres
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
  # using join query
  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
    Show.start_time <= datetime.datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(
    Show.start_time > datetime.datetime.now()).all()
  # upcoming_shows = list(filter(lambda show: show.start_time > datetime.datetime.now(), venue.shows))
  # past_shows = list(filter(lambda show: show.start_time <= datetime.datetime.now(), venue.shows))
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
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
  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    venue_form = form.data
    try:
      venue = Venue(
        name=venue_form['name'],
        genres=venue_form['genres'], # alternative: request.form.getlist('genres')
        city=venue_form['city'],
        state=venue_form['state'],
        address=venue_form['address'],
        phone=venue_form['phone'],
        image_link=venue_form['image_link'],
        facebook_link=venue_form['facebook_link'],
        website=venue_form['website_link'],
        seeking_talent=venue_form['seeking_talent'],
        seeking_description=venue_form['seeking_description'] if venue_form['seeking_description'] != '' else None,
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
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
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
      "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.datetime.now(), artist.shows)))
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
  artist_data['genres'] = artist.genres
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
  # using join query
  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time <= datetime.datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time > datetime.datetime.now()).all()
  # upcoming_shows = list(filter(lambda show: show.start_time > datetime.datetime.now(), artist.shows))
  # past_shows = list(filter(lambda show: show.start_time <= datetime.datetime.now(), artist.shows))
  upcoming_shows_count = len(upcoming_shows)
  past_shows_count = len(past_shows)
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
  artist = Artist.query.filter(Artist.id == artist_id)[0]
  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
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
        if key == 'website_link':
          artist.__setattr__('website', artist_form[key])
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
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
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
        if key == 'website_link':
          venue.__setattr__('website', venue_form[key])
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
        genres=artist_form['genres'],
        city=artist_form['city'],
        state=artist_form['state'],
        phone=artist_form['phone'],
        image_link=artist_form['image_link'],
        facebook_link=artist_form['facebook_link'],
        website=artist_form['website_link'],
        seeking_venue=artist_form['seeking_venue'],
        seeking_description=artist_form['seeking_description'] if artist_form['seeking_description'] != '' else None,
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
  error = False
  form = ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    show_form = form.data
    try:
      show = Show(
        artist_id=show_form['artist_id'],
        venue_id=show_form['venue_id'],
        start_time=show_form['start_time']
      )
      db.session.add(show)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
      return redirect(url_for('create_shows'))
    else:
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  else:
    for field, err in form.errors.items():
      for e in err:
        flash(field + ': ' + e)
    return redirect(url_for('create_shows'))

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
