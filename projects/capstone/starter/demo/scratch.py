import datetime
from models import Artist, Show, Venue
import pprint
import json
from app import db

# created_date = DateTime(datetime.datetime.utcnow)
# created_date = DateTime()
# created_date = datetime.datetime.utcnow()
created_date = datetime.datetime(2021, 1, 1, 23, 59, 59, 0)

show = Show(
    artist_id = 1,
    venue_id = 1,
    start_time = created_date)
x=8
# venue_query = Venue.query.filter(Venue.name.ilike('%' + 'dueling' + '%'))
# venue_list = []
# for venue in venue_query:
#     venue_list.append({
#         "id": venue.id,
#         "name": venue.name,
#         "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.datetime.now()).count()
#     })
#
# response = {
#     "count": len(venue_list),
#     "data": venue_list
# }

query1 = db.session.query(Show).join(Venue).filter(Show.artist_id==6).filter(Show.start_time>datetime.datetime.now()).all()
query2 = db.session.query(Show).filter(Show.artist_id==6).filter(Show.start_time>datetime.datetime.now()).all()

pp = pprint.PrettyPrinter()
pp.pprint(response)
x=8