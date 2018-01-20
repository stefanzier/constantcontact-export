from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class RetrieveCSVForm(FlaskForm):
    eventId = StringField('Event ID', validators=[DataRequired()])
    submit = SubmitField('Retrieve Registrants')
