from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.choices import RadioField, SelectMultipleField
from wtforms.fields.core import Field
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.form import Form
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, Optional
from wtforms import BooleanField, SelectField, IntegerField
from Automator.models import User
from Automator import app


class NormalFormHelper(Form):
    users = BooleanField(label="")


class NormalForm(FlaskForm):
    with app.app_context():
        users = User.query.all()

    choices = []
    for user in users:
        choices.append((user.userCode, user.userCode))

    x = FieldList(FormField(NormalFormHelper), min_entries=len(users))
    sheet = SelectField(label="Select a Sheet", validators=[DataRequired()],
                        choices=[("Dani", "Dani"), ("HS", "HS"), ("Mohammad", "Mohammad"), ("OS", "OS"),
                                 ("Pankaj", "Pankaj")])
    run = SubmitField(label="Run")


class CustomForm(FlaskForm):
    row = StringField(label='Row Number', validators=[DataRequired()])

    fields = SelectField(label="Choose a field to edit (optional)", validators=[Optional()],
                         choices=[('drname', 'drname'), ('drsigname', 'drsigname'), ('npidr', 'npidr'),
                                  ('dradd2', 'dradd2'), ('dradd3', 'dradd3'), ('dradd4', 'dradd4'),
                                  ('patname', 'patname'), ('patmed', 'patmed'), ('patadd1', 'patadd1'),
                                  ('patadd2', 'patadd2'), ('patadd3', 'patadd3'), ('patphone', 'patphone'),
                                  ('patht', 'patht'), ('patwt', 'patwt'), ('patage', 'patage'),
                                  ('patdob', 'patdob'), ('patgender', 'patgender'), ('patsizew', 'patsizew'),
                                  ('patorderdate', 'patorderdate'), ('patpaintr', 'patpaintr'),
                                  ('patpainlevel', 'patpainlevel'),
                                  ('patpainyear', 'patpainyear'), ('patpainworse', 'patpainworse'),
                                  ('patpaincause', 'patpaincause'),
                                  ('patipadd', 'patipadd'), ('patshoesize', 'patshoesize'), ('patinjury', 'patinjury'),
                                  ('patsurgery', 'patsurgery'), ('patweakness', 'patweakness'),
                                  ('pattwist', 'pattwist'),
                                  ('pattogether', 'pattogether'), ('patoneleg', 'patoneleg'), ('patbend', 'patbend'),
                                  ('pattime', 'pattime')])

    fieldUpdate = StringField(label="Submit Field")

    submitField = SubmitField(label="Submit new info")

    sheet = SelectField(label="Choose a Sheet",
                        choices=[("Dani", "Dani"), ("HS", "HS"), ("Mohammad", "Mohammad"), ("OS", "OS"),
                                 ("Pankaj", "Pankaj")])

    run = SubmitField(label="Run")

    def validate_row(self, row_to_check):
        if not row_to_check.data.isnumeric() and self.run.data:
            raise ValidationError("Please enter a valid row number")


class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Login")


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        foundUser = User.query.filter_by(username=username_to_check.data).first()
        if foundUser:
            raise ValidationError("Username already exists, please try a different one")

    username = StringField(label="Username", validators=[DataRequired(), Length(min=2, max=30)])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=6)])
    passwordConfirm = PasswordField(label="Confirm Password",
                                    validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField(label="Register")
