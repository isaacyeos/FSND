from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
import re
from datetime import date

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    release_date = DateField(
        'release_date',
        validators=[DataRequired()],
        default= date.today()
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    age = IntegerField(
        'age', validators=[DataRequired()]
    )
    gender = StringField(
        'gender', validators=[DataRequired()]
    )

