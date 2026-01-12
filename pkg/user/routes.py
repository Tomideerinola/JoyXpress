from flask import Blueprint, render_template, redirect, url_for, flash,jsonify,session, request
from pkg.models import User
from pkg.user import userobj
from .form import SignupForm,LoginForm,ProfileForm,ContactForm # import the form here
from werkzeug.security import generate_password_hash,check_password_hash
from pkg.models import db,State,City, Shipment, ShipmentStatusHistory,ContactUs # SQLAlchemy instance

@userobj.app_context_processor
def inject_user():
    user_id = session.get('useronline')
    if user_id:
        u = User.query.get(user_id)
        return dict(u=u)
    return dict(u=None)



@userobj.get('/')
def home():
    user = User.query.all()
    user_id= session.get('useronline')
    u= User.query.get(user_id)
    

    return render_template('user/index.html',user=user)


@userobj.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    # Populate states dynamically
    form.state.choices = [(s.id, s.name) for s in State.query.order_by(State.name).all()]
    form.city.choices = [(c.id, c.name) for c in City.query.filter_by(state_id=form.state.data).all()] if form.state.data else []

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
            state_id=form.state.data,
            city_id=form.city.data,
            password_hash=generate_password_hash(form.password.data)
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for('bpuser.login'))

    return render_template('user/signup.html', form=form)


@userobj.route('/cities/<int:state_id>')
def cities(state_id):
    cities = City.query.filter_by(state_id=state_id).order_by(City.name).all()
    city_list = [{"id": c.id, "name": c.name} for c in cities]
    return jsonify(city_list)




@userobj.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session["useronline"] = user.id
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for('bpuser.dashboard'))  # Your dashboard route
        else:
            flash("Invalid email or password", "danger")
    return render_template('user/login.html', form=form)



@userobj.route('/dashboard/')
def dashboard():
    user_id = session.get('useronline')
    tracking_id = request.args.get('tracking_id')


    if not user_id:
        flash("You must be logged in to access the dashboard.", "warning")
        return redirect(url_for('bpuser.login'))

    # Fetch the logged-in user
    u = User.query.get(user_id)
    if not u:
        flash("User not found. Please log in again.", "danger")
        return redirect(url_for('bpuser.logout'))

    # Fetch all shipments for this user, most recent first
    shipments = Shipment.query.filter_by(user_id=user_id).order_by(Shipment.created_at.desc()).all()
    shipment = Shipment.query.filter_by(tracking_number=tracking_id).first()


    # Calculate some stats
    total_shipments = len(shipments)
    active_shipments = [s for s in shipments if s.status.lower() in ('pending', 'in transit')]

    return render_template(
        'user/dashboard.html',
        u=u,  # logged-in user object
        shipments=shipments,
        total_shipments=total_shipments,
        active_shipments=len(active_shipments),
        user_id=user_id,shipment=shipment
    )



@userobj.route('/logout/')
def logout():
    """Logs the user out by clearing the session."""
    
    # 1. Clear the relevant session data
    # Check if the keys exist before trying to pop them
    if 'useronline' in session:
        session.pop('useronline')
        
    if 'user_full_name' in session:
        session.pop('user_full_name')

    # Optional: Clear the entire session if you have no other data you need to preserve
    # session.clear() 

    # 2. Flash a success message
    flash("You have been successfully logged out.", "info")

    # 3. Redirect to the login page (or homepage)
    # Using 'bpuser.login' ensures the link works correctly across blueprints
    return redirect(url_for('bpuser.login'))



@userobj.route('/track-shipment')
def track_shipment():
    user_id = session.get('useronline')
    u = User.query.get(user_id)

    tracking_id = request.args.get('tracking_id')

    if not tracking_id:
        flash("Please enter a tracking number.", "warning")
        return redirect(url_for('bpuser.dashboard'))

    shipment = Shipment.query.filter_by(tracking_number=tracking_id).first()

    if not shipment:
        flash("No shipment found with that tracking number.", "danger")
        return redirect(url_for('bpuser.dashboard'))

    # Optional: allow only owner to track
    user_id = session.get('useronline')
    if user_id and shipment.user_id != user_id:
        flash("You are not allowed to view this shipment.", "danger")
        return redirect(url_for('bpuser.dashboard'))

    return render_template(
        'shipment/shipment_tracking.html',
        shipment=shipment,
        title="Track Shipment",u=u
    )


@userobj.route('/org/edit/profile/')
def edit_profile():
    proform=ProfileForm()
    if session.get('useronline') != None:
        udeets=User.query.get(session['useronline'])
        proform.fullname.data=udeets.full_name #to display the email
        proform.email.data=udeets.email #to display the email
        proform.phone.data=udeets.phone #this is to display the phone munber
        return render_template('user/edit_profile.html',proform=proform,udeets=udeets)
    else:
        flash('You must be logged in to view this page', category='warning')
        return redirect(url_for('bpuser.login'))
    


@userobj.post('/update/profile/')
def update_profile():
    proform=ProfileForm()
    if session.get('useronline') !=None:
        udeets=User.query.get(session['useronline'])
        if proform.validate_on_submit():
            name=proform.fullname.data
            phone=proform.phone.data
            email=proform.email.data

            # update db via orm
            udeets.full_name=name
            udeets.phone=phone
            udeets.email=email
            db.session.commit()
            flash('Profile updated Successfully', category='success')
            return redirect(url_for('bpuser.edit_profile'))
        else:          
            return render_template('user/edit_profile.html',proform=proform,udeets=udeets)
    else:
        flash('You must be logged in to view this page', category='errormsg')
        return redirect(url_for('bpuser.login'))


            
@userobj.route('/contact/form/', methods=['GET','POST'])
def contact_form():
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
            return redirect(url_for("contact"))
        else:
            flash('Please correct the errors in the form.', 'danger ')

    return render_template('contact.html',contact=contact)