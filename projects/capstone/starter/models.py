from flask_sqlalchemy import SQLAlchemy
import seeds
from sqlalchemy import exc
import os

# database_path = os.environ['DATABASE_URL']
database_path = 'postgresql://yeo@localhost:5432/capstone'

db = SQLAlchemy()

def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

def populate_db():
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

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
    populate_db()

association_table = db.Table('association',
    db.Column('movie_id', db.Integer, db.ForeignKey('Movie.id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('Actor.id'), primary_key=True)
)

class Movie(db.Model): # change to Movie
    __tablename__ = 'Movie'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False) # change to title
    release_date = db.Column(db.Date, nullable=False)
    image_link = db.Column(db.String, nullable=False)
    actors = db.relationship('Actor', secondary=association_table,
                             backref=db.backref('movies', lazy=True))

class Actor(db.Model): # change to Actor
    __tablename__ = 'Actor'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    image_link = db.Column(db.String, nullable=False)

# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many - for many-to-many relationships
