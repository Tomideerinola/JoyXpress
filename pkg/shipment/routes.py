# pkg/shipment/routes.py (Ensure these functions are correct)

from flask import render_template, redirect, url_for, flash, session, jsonify, request
from . import shipmentobj 
from .form import NewShipmentForm
# Ensure all models are imported:
from pkg.models import State, City, User, db, Shipment, ShippingRate 
from .services import calculate_rate, generate_tracking_number 


@shipmentobj.route('/new/', methods=['GET', 'POST'])
def new_shipment():
    """Handles the creation and saving of a new shipment order."""
    
    user_id = session.get('useronline')
    u = User.query.get(user_id) if user_id else None
    shipments = Shipment.query.filter_by(user_id=user_id).order_by(Shipment.created_at.desc()).all()


    if not u:
        flash('You must be logged in to create a new shipment.', 'warning')
        return redirect(url_for('bpuser.login'))

    form = NewShipmentForm()
    
    if form.validate_on_submit():
        

        try:
            rates = calculate_rate(
                pickup_city_id=form.pickup_city.data,
                delivery_city_id=form.delivery_city.data,
                weight_kg=form.package_weight.data,
                delivery_type=form.delivery_type.data
            )
            distance = rates['distance_km']
            amount = rates['calculated_amount']
            
        except ValueError as e:
            # Catches errors from calculate_rate (e.g., missing city, missing rate tier)
            flash(f'Error calculating rate: {e}', 'danger')
            return render_template('shipment/new_shipment.html', form=form, u=u, title='Create New Shipment')
        
        # Optional: Additional check for weight/type if form validation is weak
        if distance is None or amount is None:
             flash('A calculation error prevented order creation. Check inputs.', 'danger')
             return render_template('shipment/new_shipment.html', form=form, u=u, title='Create New Shipment')


        # --- SHIPMENT DATABASE CREATION ---
        tracking_id = generate_tracking_number()
        
        # Retrieve City/State Names (Uses form IDs, which should be safe)
        # Add safety checks here to prevent crash if City.query.get() returns None
        pickup_city_obj = City.query.get(form.pickup_city.data)
        delivery_city_obj = City.query.get(form.delivery_city.data)
        pickup_state_obj = State.query.get(form.pickup_state.data)
        delivery_state_obj = State.query.get(form.delivery_state.data)
        
        if not all([pickup_city_obj, delivery_city_obj, pickup_state_obj, delivery_state_obj]):
             flash('One or more location fields contained an invalid value. Please re-select.', 'danger')
             return render_template('shipment/new_shipment.html', form=form, u=u, title='Create New Shipment')

        new_shipment = Shipment(
            tracking_number=tracking_id,
            user_id=u.id,
            receiver_name=form.receiver_name.data,
            receiver_phone=form.receiver_phone.data,
            pickup_address=form.pickup_address.data,
            pickup_city=pickup_city_obj.name,
            pickup_state=pickup_state_obj.name,
            delivery_address=form.delivery_address.data,
            delivery_city=delivery_city_obj.name,
            delivery_state=delivery_state_obj.name,
            package_weight=form.package_weight.data,
            delivery_type=form.delivery_type.data,
            distance_km=distance, # Store the calculated distance factor
            calculated_amount=amount,
            status='pending'
        )
        
        try:
            db.session.add(new_shipment)
            db.session.commit()
            
            flash(f'Shipment {tracking_id} created successfully. Proceed to payment.', 'success')
            return redirect(url_for('bpshipment.confirmation', shipment_id=new_shipment.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while saving the shipment: {str(e)}', 'danger')
            return redirect(url_for('bpshipment.new_shipment')) 

    # GET request or form validation failed
    return render_template(
        'shipment/new_shipment.html', 
        form=form, 
        u=u,
        title='Create New Shipment',shipments=shipments
    )


@shipmentobj.route('/api/cities/<int:state_id>')
def get_cities(state_id):
    """
    API endpoint to fetch cities belonging to a specific state. (STILL NEEDED FOR DROPDOWNS)
    """
    if state_id == 0:
        return jsonify([])

    cities = City.query.filter_by(state_id=state_id).order_by(City.name).all()
    city_list = [{'id': city.id, 'name': city.name} for city in cities]
    return jsonify(city_list)


# *** REMOVE THE ENTIRE api_calculate_rate ROUTE ***


# pkg/shipment/routes.py (Ensure this route exists)

@shipmentobj.route('/confirmation/<int:shipment_id>')
# @login_required # Confirmation should also be restricted to logged-in users
def confirmation(shipment_id):
    """
    Displays the shipment details and prepares for payment.
    """
    # 1. Retrieve the shipment
    shipment = Shipment.query.get_or_404(shipment_id)
    
    # 2. Security Check: Ensure the user owns the shipment
    user_id = session.get('useronline')
    u = User.query.get(user_id) if user_id else None
    
    if not u or shipment.user_id != u.id:
        flash('Access Denied or Shipment Not Found.', 'danger')
        return redirect(url_for('bpuser.dashboard'))
        
    # 3. Check if payment has already been made
    if shipment.status != 'pending':
        flash('This shipment is already processed or paid.', 'warning')
        return redirect(url_for('bpuser.dashboard'))
        
    return render_template(
        'shipment/confirmation.html',
        shipment=shipment,
        u=u,
        title="Confirm Order"
    )


@shipmentobj.route('/<int:shipment_id>')
def shipment_details(shipment_id):

    user_id = session.get('useronline')
    back_url = request.referrer or url_for('bpuser.home')

    if not user_id:
        flash("Please log in to view shipment details.", "warning")
        return redirect(url_for('bpuser.login'))

    u = User.query.get(user_id)
    shipment = Shipment.query.get_or_404(shipment_id)

    # Security check
    if shipment.user_id != user_id:
        flash("You are not allowed to view this shipment.", "danger")
        return redirect(url_for('bpuser.dashboard'))

    return render_template('shipment/shipment_tracking.html',shipment=shipment,title="Shipment Details",u=u,back_url=back_url)

@shipmentobj.route('/track/', methods=['GET', 'POST'])
def track_ship_page():
    """Renders the shipment tracking page and handles tracking requests."""
    user_id = session.get('useronline')

    u = User.query.get(user_id)

    
    tracking_id = request.args.get('tracking_id', '').strip()
    shipment = None

    if tracking_id:
        shipment = Shipment.query.filter_by(tracking_number=tracking_id).first()
        if not shipment:
            flash(f'No shipment found with Tracking ID: {tracking_id}', 'danger')

    return render_template(
        'shipment/track_shipment.html',
        shipment=shipment,
        title='Track Shipment',u=u
    )


@shipmentobj.route('/shipments/history')
def shipment_history():
    user_id = session.get('useronline')

    if not user_id:
        flash("Please log in to view your shipment history.", "warning")
        return redirect(url_for('bpuser.login'))

    # Fetch all shipments for this user
    shipments = (
        Shipment.query
        .filter_by(user_id=user_id)
        .order_by(Shipment.created_at.desc())
        .all()
    )

    return render_template(
        'shipment/shipment_history.html',
        shipments=shipments,
        title="Shipment History"
    )


@shipmentobj.route('/track/<string:tracking_number>')
def public_shipment_tracking(tracking_number):
    """
    Public route to view shipment details by tracking number (for guests and agents).
    Does NOT require login.
    """
    # Use filter_by because tracking_number is a string, then use first_or_404
    shipment = Shipment.query.filter_by(tracking_number=tracking_number).first_or_404()
    back_url = request.referrer or url_for('bpuser.home')
    
    # Check if payment is pending and redirect to confirmation page for payment
    if shipment.status == 'pending':
        # If the user is logged in, redirect them to the secure confirmation page
        user_id = session.get('useronline')
        if user_id:
            return redirect(url_for('bpshipment.confirmation', shipment_id=shipment.id))
        
        # If the user is a guest, they see a public payment required message on this tracking page
        
    return render_template(
        'shipment/public_tracking.html',
        shipment=shipment,
        title=f"Tracking: {tracking_number}",back_url=back_url
    )


@shipmentobj.route('/track', methods=['POST'])
def track_shipment():
    tracking_number = request.form.get('tracking_number')

    if not tracking_number:
        flash('Please enter a tracking number.', 'warning')
        return redirect(url_for('bpuser.home'))

    shipment = Shipment.query.filter_by(tracking_number=tracking_number).first()

    if not shipment:
        flash('Shipment not found. Please check the tracking number.', 'danger')
        return redirect(url_for('bpuser.home'))

    return redirect(
        url_for(
            'bpshipment.public_shipment_tracking',
            tracking_number=tracking_number
        )
    )