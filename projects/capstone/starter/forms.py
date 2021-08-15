from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField
from wtforms.validators import DataRequired
from datetime import date

class MovieForm(Form):
    title = StringField(
        'title', validators=[DataRequired()]
    )
    release_date = DateField(
        'release_date',
        validators=[DataRequired()],
        default= date.today()
    )
    image_link = StringField(
        'image_link', validators=[DataRequired()]
    )

class ActorForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    age = IntegerField(
        'age', validators=[DataRequired()]
    )
    gender = StringField(
        'gender', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired()]
    )
