from flask import Blueprint, render_template, redirect, url_for, flash
from pkg.models import User
from pkg.user import userobj
from .form import SignupForm  # import the form here
from werkzeug.security import generate_password_hash,check_password_hash
from pkg.models import db  # SQLAlchemy instance

@userobj.get('/')
def home():
    return render_template('user/index.html')


@userobj.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():

        # Check if user exists
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for('bpuser.login'))

        # Create user
        new_user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            city=form.city.data,
            state=form.state.data,
            password_hash=generate_password_hash(form.password.data)
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for('bpuser.login'))

    return render_template('user/signup.html', form=form)
