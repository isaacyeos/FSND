# Casting Agency API

## Capstone Project for Udacity's Full Stack Developer Nanodegree
Heroku Link: https://fsnd-isaac.herokuapp.com

While running locally: http://localhost:5000

## Getting Started

### Installing Dependencies

#### Python 3.9

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python).

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virtual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages.

## Testing the app locally

Before running the application locally, replace `DATABASE_URL` in the `setup.sh` file in root directory with the name of your local database.

If your local database hasn't yet been created, run the following:
```
createdb capstone
flask db upgrade
```

To reset the database to a clean slate, run the following:
```
dropdb capstone && createdb capstone
flask db upgrade
```

To run the server, execute:

```bash
chmod +x setup.sh
./setup.sh
flask run --reload
```

The script `setup.sh` will set up all necessary environment variables. This includes setting the `FLASK_APP` variable to `app.py` which directs flask to use the `app.py` file to find the application. 

Using the `--reload` flag will detect file changes and restart the server automatically.

To run unit tests locally, run the following:
```
python -m unittest test.py
```

If all tests pass, the output should be the following:
```
```

## Testing the hosted app

A postman collection is available to test the hosted app. Import `capstone.postman_collection.json` into Postman, and run the collection.

## API Reference

Authentication: This application requires authentication to perform various actions. All the endpoints require
various permissions, except the root (index) endpoint. The permissions are passed via the `Bearer` token.

The application has two different types of roles:
- Assistant
  - can only view the list of artists/movies and complete information for any actor/movie
  - has `get:actors, get:movies` permissions
- Director
  - can perform all the actions that `Assistant` can
  - can create/update/delete any actor/movie 
  - has `get:actors, get:movies, patch:actors, patch:movies, post:actors, post:movies, delete:actors, delete:movies`

## Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": false,
    "error": 404,
    "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
}
```

The API will return the following errors based on how the request fails:
 - 400: Bad Request
 - 401: Unauthorized
 - 403: Forbidden
 - 404: Not Found
 - 405: Method Not Allowed
 - 422: Unprocessable Entity
 - 500: Internal Server Error

## Endpoints

#### GET /
 - General
   - root endpoint
   - used to check if the api is up and running
   - is a public endpoint, requires no authentication
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/`

<details>
<summary>Sample Response</summary>

```
{
   "success": true
}
```

</details>

#### GET /actors
 - General
   - gets the list of all the actors
   - requires `get:actors` permission
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/actors`

<details>
<summary>Sample Response</summary>

```
{
    "actors": [
        "Chris Evans",
        "Chris Hemsworth",
        "Mark Ruffalo"
    ],
    "success": true
}
```

</details>

#### GET /actors/{actor_id}
 - General
   - gets the complete info for an actor by id
   - requires `get:actors` permission
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/actors/1`

<details>
<summary>Sample Response</summary>

```
{
    "actor": "Chris Evans",
    "actor_id": 1,
    "movies": [],
    "success": true
}
```
  
</details>

#### POST /actors
 - General
   - creates a new actor
   - requires `post:actors` permission
 
 - Request Body
   - name: string, required
   - age: integer, required
   - gender: string, required
   - image_link: string, required
   - movies: list of strings, required

 - NOTE
   - Movies passed in the `movies` list in request body must already exist in the database prior to making this request.
   - If not, the movie will not be added to the actor's list of movies
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/actors`
   - Request Body
     ```
     {
        "name": "Robert Downey Jr.",
        "age": 56,
        "gender": "M",
        "image_link": "https://upload.wikimedia.org/wikipedia/commons/9/94/Robert_Downey_Jr_2014_Comic_Con_%28cropped%29.jpg",
        "movies": ["Avengers"]
      }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "actor": "Robert Downey Jr.",
    "actor_id": 4,
    "movies": [
        "Avengers"
    ],
    "success": true
}
```
  
</details>

#### PATCH /actors/{actor_id}
 - General
   - updates the info for an actor
   - requires `patch:actors` permission
 
 - Request Body
   - name: string, required
   - age: integer, required
   - gender: string, required
   - image_link: string, required
   - movies: list of strings, required

- NOTE
   - Movies passed in the `movies` list in request body will completely replace the existing relationship.
   - So, if you want to append new movies to an actor, pass the existing movies also in the request.
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/actors/1`
   - Request Body
     ```
      {
          "name": "Christopher Robert Evans",
          "age": 40,
          "gender": "M",
          "image_link": "https://upload.wikimedia.org/wikipedia/commons/3/33/Mark_Kassen%2C_Tony_C%C3%A1rdenas_and_Chris_Evans_%28cropped%29.jpg",
          "movies": ["Avengers", "Captain America"]
      }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "actor": "Christopher Robert Evans",
    "actor_id": 1,
    "movies": [
        "Captain America",
        "Avengers",
    ],
    "success": true
}
```
  
</details>

#### DELETE /actors/{actor_id}
 - General
   - deletes the actor
   - requires `delete:actors` permission
   - will also delete the mapping to the movie but will not delete the movie from the database
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/actors/4`

<details>
<summary>Sample Response</summary>

```
{
    "actor": "Robert Downey Jr.",
    "actor_id": 4,
    "success": true
}
```
  
</details>

#### GET /movies
 - General
   - gets the list of all the movies
   - requires `get:movies` permission
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/movies`

<details>
<summary>Sample Response</summary>

```
{
    "movies": [
        "Captain America",
        "Avengers"
    ],
    "success": true
}
```

</details>

#### GET /movies/{movie_id}
 - General
   - gets the complete info for a movie by id
   - requires `get:movies` permission
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/movies/1`

<details>
<summary>Sample Response</summary>

```
{
    "actors": [],
    "movie": "Avengers",
    "movie_id": 1,
    "success": true
}
```
  
</details>

#### POST /movies
 - General
   - creates a new movie
   - requires `post:movies` permission
 
 - Request Body
   - title: string, required
   - release_date: string in date format, required
   - image_link: string, required
   - actors: list of strings, required
 
 - NOTE
   - Actors passed in the `actors` list in request body must already exist in the database prior to making this request.
   - If not, the actor will not be added to the movie's list of actors
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/movies`
   - Request Body
     ```
      {
          "title": "Avengers Endgame",
          "release_date": "2019-01-01",
          "image_link": "https://upload.wikimedia.org/wikipedia/en/0/0d/Avengers_Endgame_poster.jpg",
          "actors": ["Chris Evans", "Mark Ruffalo"]
      }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "actors": [
        "Chris Evans",
        "Mark Ruffalo"
    ],
    "movie": "Avengers Endgame",
    "movie_id": 3,
    "success": true
}
```
  
</details>

#### PATCH /movie/{movie_id}
 - General
   - updates the info for a movie
   - requires `patch:movies` permission
 
 - Request Body
   - title: string, required
   - release_date: string in date format, required
   - image_link: string, required
   - actors: list of strings, required
 
 - NOTE
   - Actors passed in the `actors` list in request body will completely replace the existing relationship.
   - So, if you want to append new actors to a movie, pass the existing actors also in the request.
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/movies/1`
   - Request Body
     ```
      {
          "title": "Avengers",
          "release_date": "2021-01-01",
          "image_link": "https://upload.wikimedia.org/wikipedia/en/8/8a/The_Avengers_%282012_film%29_poster.jpg",
          "actors": ["Chris Hemsworth", "Mark Ruffalo"]
      }
     ```

<details>
<summary>Sample Response</summary>

```
{
    "actors": [
        "Chris Hemsworth",
        "Mark Ruffalo"
    ],
    "movie": "Avengers",
    "movie_id": 1,
    "success": true
}
```
  
</details>

#### DELETE /movies/{movie_id}
 - General
   - deletes the movie
   - requires `delete:movies` permission
   - will not affect the actors present in the database
 
 - Sample Request
   - `https://fsnd-isaac.herokuapp.com/movies/3`

<details>
<summary>Sample Response</summary>

```
{
    "movie": "Avengers Endgame",
    "movie_id": 3,
    "success": true
}
```
  
</details>
