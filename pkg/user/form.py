from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, TelField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from pkg.models import State, City

class SignupForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=6, max=20)])
    state = SelectField("State", coerce=int, validators=[DataRequired()])
    city = SelectField("City", coerce=int, validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Populate states
    self.state.choices = [(str(s.id), s.state_name) for s in State.query.order_by(State.state_name).all()]
    # Optionally: populate cities for the first state as default
    if self.state.choices:
        first_state_id = int(self.state.choices[0][0])
        self.city.choices = [(str(c.id), c.city_name) for c in City.query.filter_by(state_id=first_state_id).order_by(City.city_name).all()]



class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Enter a valid email")
        ],
        render_kw={"placeholder": "Enter your email"}
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required"),
            Length(min=4, message="Password must be at least 6 characters")
        ],
        render_kw={"placeholder": "Enter your password"}
    )

    submit = SubmitField("Login")



class ProfileForm(FlaskForm):
    fullname = StringField('FullName', validators=[DataRequired(), Length(min=2, max=100)])
    phone = TelField("Phone Number", validators=[DataRequired(), Length(min=5, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')