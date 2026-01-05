from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class SignupForm(FlaskForm):
    full_name = StringField(
        "Full Name", 
        validators=[DataRequired(message="Full name is required"), Length(min=2, max=120)]
    )
    email = EmailField(
        "Email", 
        validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email")]
    )
    phone = StringField(
        "Phone Number", 
        validators=[DataRequired(message="Phone number is required"), Length(min=6, max=20)]
    )
    city = StringField(
        "City", 
        validators=[DataRequired(message="City is required"), Length(min=2, max=100)]
    )
    state = StringField(
        "State", 
        validators=[DataRequired(message="State is required"), Length(min=2, max=100)]
    )
    password = PasswordField(
        "Password", 
        validators=[DataRequired(message="Password is required"), Length(min=6)]
    )
    confirm_password = PasswordField(
        "Confirm Password", 
        validators=[
            DataRequired(message="Confirm your password"),
            EqualTo('password', message="Passwords must match")
        ]
    )
    submit = SubmitField("Sign Up")