import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://{}:{}@{}/{}".format('yeo', '','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is the meaning of life?',
            'answer': 'The pursuit of happiness',
            'category': 2,
            'difficulty': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['questions']), 10)

    def test_get_paginated_questions_2(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['questions']), 9)

    def test_create_new_question(self):
        res = self.client().post('/questions?page=2', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
        # self.assertTrue(data['created'] == 24)
        # self.assertTrue(data['total_questions'] == 20)
        # self.assertTrue(len(data['questions']) == 10)

    def test_get_question_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'expressionism'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 1)

    def test_get_question_search_with_results_2(self):
        res = self.client().post('/questions', json={'searchTerm': 'world cup'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 2)

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'avengers'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)

    def test_get_questions_by_category(self):
        res = self.client().get('categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['totalQuestions'], 4)
        self.assertEqual(data['currentCategory'], 'History')

    def test_delete_question(self):
        res = self.client().delete('/questions/34')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 34)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 19)

    def test_next_question(self):
        res = self.client().post('/quizzes', json={'previous_questions': [1, 4, 20, 15],
                                                   'quiz_category': 'Entertainment'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_422_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_422_delete_nonexistent_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_404_delete_question_invalid_param(self):
        res = self.client().delete('/questions/hello')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_422_get_question_from_nonexistent_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_422_get_invalid_next_question(self):
        res = self.client().post('/quizzes', json={'previous_questions': [1, 4, 20, 15],
                                                   'quiz_category': 'Hello World'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_422_get_invalid_next_question_2(self):
        res = self.client().post('/quizzes', json={'previous_questions': [i for i in range(50)],
                                                   'quiz_category': 'Entertainment'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_500_get_invalid_next_question_3(self):
        res = self.client().post('/quizzes', json={'previous_questions': [i for i in range(50)],
                                                   'quiz_category': {'key' : 'value'}})
        # this will cause a type mismatch in Question.query.filter as we will match a str type to a dict type
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'internal server error')

    # following test works if a non-null constraint was set on the database fields
    # def test_422_create_invalid_question(self):
    #     invalid_question = {
    #         'question': 'What is the meaning of life?',
    #         'answer' : None
    #     }
    #     res = self.client().post('/questions', json=invalid_question)
    #     data = json.loads(res.data)
    #
    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()