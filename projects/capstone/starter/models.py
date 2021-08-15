from app import db

association_table = db.Table('association',
    db.Column('movie_id', db.Integer, db.ForeignKey('Movie.id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('Actor.id'), primary_key=True)
)

class Movie(db.Model): # change to Movie
    __tablename__ = 'Movie'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False) # change to title
    release_date = db.Column(db.Date, nullable=False)
    image_link = db.Column(db.String, nullable=True)
    actors = db.relationship('Actor', secondary=association_table,
                             backref=db.backref('movies', lazy=True))

class Actor(db.Model): # change to Actor
    __tablename__ = 'Actor'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    image_link = db.Column(db.String, nullable=True)

# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many - for many-to-many relationships
