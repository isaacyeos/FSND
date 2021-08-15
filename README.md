Notes from Udacity's Full-Stack Nanodegree program.

## Creating a postgres database and running Flask migrations
In this example, fyyur is the name of the database we will create. Add database url to SQLALCHEMY_DATABASE_URI. 
```
SQLALCHEMY_DATABASE_URI = 'postgresql://yeo@localhost:5432/fyyur'
```

Next, create the database.
```
createdb fyyur
```
Once the database is created, we can initialize our migrations.
Create initial migrations directory structure.
```
flask db init
```
Sync models.
```
flask db migrate
```
To create tables in database
```
flask db upgrade
```
