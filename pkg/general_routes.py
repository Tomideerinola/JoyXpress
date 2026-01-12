from flask import render_template,session,url_for,request,redirect,flash
from pkg import app
from pkg.models import db, User, State, City,ContactUs
from pkg.user.form import ContactForm

@app.get('/')
def home_page():
    user = User.query.all()
    user_id= session.get('useronline')
    u= User.query.get(user_id)
    return render_template('index.html',user=user,u=u,user_id=user_id)


@app.get('/oldindex/')
def landing_page():
    return render_template('indext.html')


@app.get('/about/')
def about_page():
    user_id= session.get('useronline')

    return render_template('about.html',user_id=user_id)


@app.get('/service/')
def service():
    user_id= session.get('useronline')

    return render_template('service.html',user_id=user_id)

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    user_id= session.get('useronline')

    contact= ContactForm()

    if request.method == 'POST':
        if contact.validate_on_submit():
            name= contact.name.data
            email = contact.email.data
            message= contact.message.data
            contact_method=contact.contact_method.data
            phone = contact.phone.data

            co=ContactUs(name=name,email=email,message=message,contact_method=contact_method,phone=phone)
            db.session.add(co)
            db.session.commit()
            flash('Your Message has been received and we will get back to you Shortly', 'success ')
            return redirect(url_for("contact"))
        else:
            flash('Please correct the errors in the form.', 'danger ')
    return render_template('contact.html',contact=contact,user_id=user_id)