from app import db

class Venue(db.Model): # change to Movie
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False) # change to title
    release_date = db.Column(db.Date, nullable=False)

class Artist(db.Model): # change to Actor
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)