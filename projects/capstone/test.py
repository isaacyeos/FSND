import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import datetime

from app import create_app
import os

class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the Casting Agency test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.assistant_token = os.environ['assistant_token']
        self.director_token = os.environ['director_token']
        self.app = create_app()
        self.client = self.app.test_client

        self.new_movie = {
            'title': 'Avengers Endgame',
            'release_date': datetime.datetime(2019, 1, 1),
            'image_link': 'https://upload.wikimedia.org/wikipedia/en/0/0d/Avengers_Endgame_poster.jpg',
            'actors': ['Chris Evans', 'Mark Ruffalo']
        }

        self.invalid_movie_422_1 = {}

        self.invalid_movie_422_2 = {
            'title': 'Avengers Endgame',
            'release_date': None,
            'image_link': None,
            'actors': ['Chris Evans', 'Mark Ruffalo']
        }

        self.update_movie = {
            'title': 'Avengers',
            'release_date': datetime.datetime(2012, 1, 1),
            'image_link': 'https://upload.wikimedia.org/wikipedia/en/8/8a/The_Avengers_%282012_film%29_poster.jpg',
            'actors': ['Chris Hemsworth', 'Mark Ruffalo']
        }

        self.new_actor = {
            'name': 'Robert Downey Jr.',
            'age': 56,
            'gender': 'M',
            'image_link': 'https://upload.wikimedia.org/wikipedia/commons/9/94/Robert_Downey_Jr_2014_Comic_Con_%28cropped%29.jpg',
            'movies': ['Avengers']
        }

        self.invalid_actor_422_1 = {}

        self.invalid_actor_422_2 = {
            'name': None,
            'age': 56,
            'gender': 'M',
            'image_link': 'https://upload.wikimedia.org/wikipedia/commons/9/94/Robert_Downey_Jr_2014_Comic_Con_%28cropped%29.jpg',
            'movies': ['Avengers']
        }

        self.update_actor = {
            'name': 'Chris Evans',
            'age': 40,
            'gender': 'M',
            'image_link': 'https://upload.wikimedia.org/wikipedia/commons/3/33/Mark_Kassen%2C_Tony_C%C3%A1rdenas_and_Chris_Evans_%28cropped%29.jpg',
            'movies': ['Avengers', 'Captain America']
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    def test_index(self):
        res = self.client().get('/')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)

    def test_get_movies_without_token(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Authorization header is expected.")

    def test_get_movies(self):
        res = self.client().get('/movies', headers={
            'Authorization': "Bearer {}".format(self.assistant_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data["success"])
        self.assertIn('movies', data)
        self.assertTrue(len(data["movies"]))

    def test_get_movie_by_id(self):
        res = self.client().get('/movies/1', headers={
            'Authorization': "Bearer {}".format(self.assistant_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('movie_id', data)
        self.assertIn('movie', data)
        self.assertIn('actors', data)

    def test_404_get_movie_by_id(self):
        res = self.client().get('/movies/100', headers={
            'Authorization': "Bearer {}".format(self.assistant_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "no such movie exists")

    def test_403_create_movie(self):
        res = self.client().post('/movies', headers={
            'Authorization': "Bearer {}".format(self.assistant_token)
        }, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Unauthorized. Permission not found.")

    def test_create_movie(self):
        res = self.client().post('/movies', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('movie_id', data)
        self.assertIn('movie', data)
        self.assertIn('actors', data)
        self.assertTrue(len(data["actors"]) == len(self.new_movie["actors"]))
        for actor in self.new_movie['actors']:
            self.assertTrue(actor in data['actors'])

    def test_422_create_movie_1(self):
        res = self.client().post('/movies', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.invalid_movie_422_1)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "invalid json parameters")

    def test_422_create_movie_2(self):
        res = self.client().post('/movies', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.invalid_movie_422_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "invalid json parameters")

    def test_update_movie(self):
        res = self.client().patch('/movies/1', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.update_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('movie_id', data)
        self.assertIn('movie', data)
        self.assertIn('actors', data)
        for actor in self.update_movie['actors']:
            self.assertTrue(actor in data['actors'])

    def test_422_update_movie_1(self):
        res = self.client().patch('/movies/1', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.invalid_movie_422_1)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "invalid json parameters")

    def test_422_update_movie_2(self):
        res = self.client().patch('/movies/1', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.invalid_movie_422_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "invalid json parameters")

    def test_delete_movie(self):
        res = self.client().delete('/movies/1', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data['movie_id'], 1)
        self.assertIn('movie', data)

    def test_404_delete_movie(self):
        res = self.client().delete('/movies/100', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no such movie exists')

    def test_get_actors(self):
        res = self.client().get('/actors', headers={
            'Authorization': "Bearer {}".format(self.assistant_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertTrue(data["success"])
        self.assertIn('actors', data)
        self.assertTrue(len(data["actors"]))

    def test_get_actor_by_id(self):
        res = self.client().get('/actors/1', headers={
            'Authorization': "Bearer {}".format(self.assistant_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('actor_id', data)
        self.assertIn('actor', data)
        self.assertIn('movies', data)

    def test_404_get_actor_by_id(self):
        res = self.client().get('/actors/100', headers={
            'Authorization': "Bearer {}".format(self.assistant_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "no such actor exists")

    def test_403_create_actor(self):
        res = self.client().post('/actors', headers={
            'Authorization': "Bearer {}".format(self.assistant_token)
        }, json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Unauthorized. Permission not found.")

    def test_create_actor(self):
        res = self.client().post('/actors', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('actor_id', data)
        self.assertIn('actor', data)
        self.assertIn('movies', data)
        self.assertTrue(len(data["movies"]) == len(self.new_actor["movies"]))
        for movie in self.new_actor['movies']:
            self.assertTrue(movie in data['movies'])

    def test_422_create_actor_1(self):
        res = self.client().post('/actors', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.invalid_actor_422_1)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "invalid json parameters")

    def test_422_create_actor_2(self):
        res = self.client().post('/actors', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.invalid_actor_422_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "invalid json parameters")

    def test_update_actor(self):
        res = self.client().patch('/actors/1', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.update_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn('actor_id', data)
        self.assertIn('actor', data)
        self.assertIn('movies', data)
        for movie in self.update_actor['movies']:
            self.assertTrue(movie in data['movies'])

    def test_422_update_actor_1(self):
        res = self.client().patch('/actors/1', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.invalid_actor_422_1)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "invalid json parameters")

    def test_422_update_actor_2(self):
        res = self.client().patch('/actors/1', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        }, json=self.invalid_actor_422_2)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "invalid json parameters")

    def test_delete_actor(self):
        res = self.client().delete('/actors/1', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data['actor_id'], 1)
        self.assertIn('actor', data)

    def test_404_delete_actor(self):
        res = self.client().delete('/actors/100', headers={
            'Authorization': "Bearer {}".format(self.director_token)
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'no such actor exists')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()