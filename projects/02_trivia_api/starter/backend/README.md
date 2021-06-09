# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.9** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by navigating to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore the database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```
This database is set to have the Owner 'yeo'. Change the trivia.psql script accordingly to use your postgresql username.

### Running the server

To run the server in development mode, execute the following.

For Mac/Linux:
```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

For Windows:
```bash
set FLASK_APP=flaskr
set FLASK_ENV=development
flask run
```

## API Reference
### Endpoints 
#### GET /categories
- General:
    - Returns a dictionary of mappings from category ID to category type
- Sample: `curl http://127.0.0.1:5000/categories`

``` 
{'categories': {'1': 'Science',
                '2': 'Art',
                '3': 'Geography',
                '4': 'History',
                '5': 'Entertainment',
                '6': 'Sports'}}
```

#### GET /questions
- General:
    - Returns a list of all available categories, list of questions on the page, success value, and total number of questions
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1. 
- Samples: 
<br>`curl http://127.0.0.1:5000/questions` (will default to page 1)
<br>`curl http://127.0.0.1:5000/questions?page=2`

``` 
{'categories': {'1': 'Science',
                '2': 'Art',
                '3': 'Geography',
                '4': 'History',
                '5': 'Entertainment',
                '6': 'Sports'},
 'questions': [{'answer': 'Apollo 13',
                'category': 5,
                'difficulty': 4,
                'id': 2,
                'question': 'What movie earned Tom Hanks his third straight '
                            'Oscar nomination, in 1996?'},
               {'answer': 'Tom Cruise',
                'category': 5,
                'difficulty': 4,
                'id': 4,
                'question': 'What actor did author Anne Rice first denounce, '
                            'then praise in the role of her beloved Lestat?'},
               {'answer': 'Maya Angelou',
                'category': 4,
                'difficulty': 2,
                'id': 5,
                'question': "Whose autobiography is entitled 'I Know Why the "
                            "Caged Bird Sings'?"},
               {'answer': 'Edward Scissorhands',
                'category': 5,
                'difficulty': 3,
                'id': 6,
                'question': 'What was the title of the 1990 fantasy directed '
                            'by Tim Burton about a young man with multi-bladed '
                            'appendages?'},
               {'answer': 'Muhammad Ali',
                'category': 4,
                'difficulty': 1,
                'id': 9,
                'question': "What boxer's original name is Cassius Clay?"},
               {'answer': 'Brazil',
                'category': 6,
                'difficulty': 3,
                'id': 10,
                'question': 'Which is the only team to play in every soccer '
                            'World Cup tournament?'},
               {'answer': 'Uruguay',
                'category': 6,
                'difficulty': 4,
                'id': 11,
                'question': 'Which country won the first ever soccer World Cup '
                            'in 1930?'},
               {'answer': 'George Washington Carver',
                'category': 4,
                'difficulty': 2,
                'id': 12,
                'question': 'Who invented Peanut Butter?'},
               {'answer': 'Lake Victoria',
                'category': 3,
                'difficulty': 2,
                'id': 13,
                'question': 'What is the largest lake in Africa?'},
               {'answer': 'The Palace of Versailles',
                'category': 3,
                'difficulty': 3,
                'id': 14,
                'question': 'In which royal palace would you find the Hall of '
                            'Mirrors?'}],
 'success': True,
 'total_questions': 19}
```
#### DELETE /questions/{question_id}
- General:
    - Deletes the question of the given ID if it exists. Returns the id of the deleted question, success value, total questions, and question list based on current page number to update the frontend. 
- Sample: `curl -X DELETE http://127.0.0.1:5000/books/33?page=1`
```
{'deleted': 33,
 'questions': [{'answer': 'Apollo 13',
                'category': 5,
                'difficulty': 4,
                'id': 2,
                'question': 'What movie earned Tom Hanks his third straight '
                            'Oscar nomination, in 1996?'},
               {'answer': 'Tom Cruise',
                'category': 5,
                'difficulty': 4,
                'id': 4,
                'question': 'What actor did author Anne Rice first denounce, '
                            'then praise in the role of her beloved Lestat?'},
               {'answer': 'Maya Angelou',
                'category': 4,
                'difficulty': 2,
                'id': 5,
                'question': "Whose autobiography is entitled 'I Know Why the "
                            "Caged Bird Sings'?"},
               {'answer': 'Edward Scissorhands',
                'category': 5,
                'difficulty': 3,
                'id': 6,
                'question': 'What was the title of the 1990 fantasy directed '
                            'by Tim Burton about a young man with multi-bladed '
                            'appendages?'},
               {'answer': 'Muhammad Ali',
                'category': 4,
                'difficulty': 1,
                'id': 9,
                'question': "What boxer's original name is Cassius Clay?"},
               {'answer': 'Brazil',
                'category': 6,
                'difficulty': 3,
                'id': 10,
                'question': 'Which is the only team to play in every soccer '
                            'World Cup tournament?'},
               {'answer': 'Uruguay',
                'category': 6,
                'difficulty': 4,
                'id': 11,
                'question': 'Which country won the first ever soccer World Cup '
                            'in 1930?'},
               {'answer': 'George Washington Carver',
                'category': 4,
                'difficulty': 2,
                'id': 12,
                'question': 'Who invented Peanut Butter?'},
               {'answer': 'Lake Victoria',
                'category': 3,
                'difficulty': 2,
                'id': 13,
                'question': 'What is the largest lake in Africa?'},
               {'answer': 'The Palace of Versailles',
                'category': 3,
                'difficulty': 3,
                'id': 14,
                'question': 'In which royal palace would you find the Hall of '
                            'Mirrors?'}],
 'success': True,
 'total_questions': 19}
```

#### POST /questions
- General:
    - Creates a new question using the submitted question, answer, category and difficulty. Returns the id of the created question, success value, total questions, and question list based on current page number to update the frontend. 
- Sample: `curl http://127.0.0.1:5000/questions?page=2 -X POST -H "Content-Type: application/json" -d '{"question":"What is the meaning of life?", "answer":"The pursuit of happiness", "category":2, "difficulty":1}'`
```
{'created': 35,
 'questions': [{'answer': 'Agra',
                'category': 3,
                'difficulty': 2,
                'id': 15,
                'question': 'The Taj Mahal is located in which Indian city?'},
               {'answer': 'Escher',
                'category': 2,
                'difficulty': 1,
                'id': 16,
                'question': 'Which Dutch graphic artist–initials M C was a '
                            'creator of optical illusions?'},
               {'answer': 'Mona Lisa',
                'category': 2,
                'difficulty': 3,
                'id': 17,
                'question': 'La Giaconda is better known as what?'},
               {'answer': 'One',
                'category': 2,
                'difficulty': 4,
                'id': 18,
                'question': 'How many paintings did Van Gogh sell in his '
                            'lifetime?'},
               {'answer': 'Jackson Pollock',
                'category': 2,
                'difficulty': 2,
                'id': 19,
                'question': 'Which American artist was a pioneer of Abstract '
                            'Expressionism, and a leading exponent of action '
                            'painting?'},
               {'answer': 'The Liver',
                'category': 1,
                'difficulty': 4,
                'id': 20,
                'question': 'What is the heaviest organ in the human body?'},
               {'answer': 'Alexander Fleming',
                'category': 1,
                'difficulty': 3,
                'id': 21,
                'question': 'Who discovered penicillin?'},
               {'answer': 'Scarab',
                'category': 4,
                'difficulty': 4,
                'id': 23,
                'question': 'Which dung beetle was worshipped by the ancient '
                            'Egyptians?'},
               {'answer': 'world',
                'category': 1,
                'difficulty': 3,
                'id': 32,
                'question': 'hello'},
               {'answer': 'The pursuit of happiness',
                'category': 2,
                'difficulty': 1,
                'id': 35,
                'question': 'What is the meaning of life?'}],
 'success': True,
 'total_questions': 20}
```

#### GET /categories/{category_id}/questions
- General:
    - Gets questions belonging to the specified category ID. Returns the success value, total questions, selected category type, and question list based on current page number to update the frontend. 
- Sample: `curl http://127.0.0.1:5000/categories/4/questions`
```
{
  "currentCategory": "History",
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Scarab",
      "category": 4,
      "difficulty": 4,
      "id": 23,
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }
  ],
  "success": true,
  "totalQuestions": 4
}
```

#### POST /questions
- General:
    - Gets questions based on a search term. Returns any questions for whom the search term is a substring of the question. Returns the success value, total questions, and question list based on current page number to update the frontend. 
- Sample: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"searchTerm":"world cup"}'`
```
{
  "questions": [
    {
      "answer": "Brazil",
      "category": 6,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    },
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }
  ],
  "success": true,
  "total_questions": 2
}
```

#### POST /quizzes
- General:
    - Gets questions to play the quiz. Takes category and previous question parameters and returns a random question within the given category (if not provided, defaults to Science), and that is not one of the previous questions. 
- Sample: `curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions": [1, 4, 20, 15], "quiz_category": "Entertainment"}'` (Remember to enclose all json keys and values in double quotes)
```
{
  "question": {
    "answer": "Apollo 13",
    "category": 5,
    "difficulty": 4,
    "id": 2,
    "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
  }
}
```

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 404,
    "message": "resource not found"
}
```
The API will return three error types when requests fail:
- 404: resource not found
- 422: unprocessable
- 500: internal server error

## Testing
To run unit tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
