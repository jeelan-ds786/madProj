from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('professional', 'Professional')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

class ServiceRequestForm(FlaskForm):
    service_id = SelectField('Service', coerce=int, choices=[], validators=[DataRequired()])
    date_of_request = DateTimeField('Date of Request', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit = SubmitField('Request Service')
