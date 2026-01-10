from flask import render_template,flash,redirect,url_for,request,session
from pkg.admin import adminobj
from werkzeug.security import generate_password_hash,check_password_hash
from pkg.models import db, State, City, ShippingRate,Admin, Agent, User, Shipment,Payment,ShipmentStatusHistory
from .form import AdminLoginForm
from .utils import generate_temp_password
from datetime import datetime


NIGERIA_LOCATIONS = {
    "Abia": ["Aba", "Umuahia", "Ohafia", "Arochukwu"],
    "Adamawa": ["Yola", "Mubi", "Numan", "Ganye"],
    "Akwa Ibom": ["Uyo", "Ikot Ekpene", "Eket", "Oron"],
    "Anambra": ["Awka", "Onitsha", "Nnewi", "Ekwulobia"],
    "Bauchi": ["Bauchi", "Azare", "Misau", "Jama’are"],
    "Bayelsa": ["Yenagoa", "Ogbia", "Brass", "Nembe"],
    "Benue": ["Makurdi", "Gboko", "Otukpo", "Katsina-Ala"],
    "Borno": ["Maiduguri", "Biu", "Dikwa", "Gwoza"],
    "Cross River": ["Calabar", "Ikom", "Ogoja", "Obudu"],
    "Delta": ["Asaba", "Warri", "Sapele", "Ughelli"],
    "Ebonyi": ["Abakaliki", "Afikpo", "Onueke"],
    "Edo": ["Benin City", "Auchi", "Ekpoma"],
    "Ekiti": ["Ado-Ekiti", "Ikere", "Omuo"],
    "Enugu": ["Enugu", "Nsukka", "Awgu", "Udi"],
    "Gombe": ["Gombe", "Kaltungo", "Dukku"],
    "Imo": ["Owerri", "Orlu", "Okigwe"],
    "Jigawa": ["Dutse", "Hadejia", "Gumel"],
    "Kaduna": ["Kaduna", "Zaria", "Kafanchan"],
    "Kano": ["Kano", "Wudil", "Rano", "Gaya"],
    "Katsina": ["Katsina", "Daura", "Funtua"],
    "Kebbi": ["Birnin Kebbi", "Argungu", "Yauri"],
    "Kogi": ["Lokoja", "Okene", "Idah"],
    "Kwara": ["Ilorin", "Offa", "Omu-Aran"],
    "Lagos": ["Ikeja", "Lekki", "Yaba", "Surulere", "Ikorodu", "Badagry"],
    "Nasarawa": ["Lafia", "Keffi", "Akwanga"],
    "Niger": ["Minna", "Bida", "Suleja"],
    "Ogun": ["Abeokuta", "Ijebu-Ode", "Ota", "Sagamu"],
    "Ondo": ["Akure", "Owo", "Ondo", "Ikare"],
    "Osun": ["Osogbo", "Ile-Ife", "Ilesa"],
    "Oyo": ["Ibadan", "Ogbomosho", "Oyo", "Iseyin"],
    "Plateau": ["Jos", "Bukuru", "Pankshin"],
    "Rivers": ["Port Harcourt", "Obio-Akpor", "Bonny", "Ahoada"],
    "Sokoto": ["Sokoto", "Wamako", "Tambuwal"],
    "Taraba": ["Jalingo", "Wukari", "Takum"],
    "Yobe": ["Damaturu", "Potiskum", "Gashua"],
    "Zamfara": ["Gusau", "Kaura Namoda", "Talata Mafara"],
    "FCT": ["Abuja", "Garki", "Wuse", "Maitama", "Kubwa"]
}

VEHICLE_TYPES = ["bike", "car", "van", "truck"]

def admin_login_required(f):
    from functools import wraps
    from flask import g
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_online"):
            flash("Please log in as admin.", "warning")
            return redirect(url_for("bpadmin.admin_login"))
        return f(*args, **kwargs)
    return decorated_function


@adminobj.route('/')
def home():
    return render_template('admin/index.html')


@adminobj.route('/dashboard')
def dashboard():
    total_shipments = Shipment.query.count()
    delivered = Shipment.query.filter_by(status='delivered').count()
    transit = Shipment.query.filter_by(status='transit').count()
    pending = Shipment.query.filter_by(status='pending').count()

    total_users = User.query.count()
    total_agents = Agent.query.count()
    recent_shipments = Shipment.query.order_by(Shipment.created_at.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        total_shipments=total_shipments,
        delivered=delivered,
        transit=transit,
        pending=pending,
        total_users=total_users,
        total_agents=total_agents,
        title="Admin Dashboard",recent_shipments=recent_shipments
    )


    # This is my admin login route 
@adminobj.route('/admin/login/', methods=['POST', 'GET'])
def admin_login():
    adminloginform=AdminLoginForm()
    if request.method=='GET':
        return render_template('admin/admin_login.html',adminloginform=adminloginform)
    else:
        if adminloginform.validate_on_submit(): #this is where they login and i validate thier details
            username=adminloginform.username.data
            password=adminloginform.password.data
            admin_details=Admin.query.filter(Admin.admin_username==username).first()

            if admin_details: #means the username is correct and they can proceed 
                stored_password=admin_details.admin_pwd
                check_password= check_password_hash(stored_password,password)
                if check_password ==True:
                    session.clear()
                    session['adminonline']=admin_details.admin_id
                    return redirect(url_for('bpadmin.dashboard'))
                else: #comes here if the password is wrong 
                    flash('Invalid Login Password', category='error')
                    return redirect(url_for('bpadmin.admin_login'))
            else: #come to this if the username is wrong 
                flash('Invalid Username, Try Again', category='error')
                return redirect(url_for('bpadmin.admin_login'))
        else:
            return render_template('admin/admin_login.html',adminloginform=adminloginform)


        # this is my admin logout route
@adminobj.route('/admin/logout/', methods=['POST', 'GET'])
def admin_logout():
    if session.get('adminonline')!=None:
        session.pop('adminonline')   
    return redirect('/admin/login/')


@adminobj.route('/shipments')
def view_all_shipments():
    # Get optional status filter from query params
    status_filter = request.args.get('status') 

    # Base query
    query = Shipment.query.order_by(Shipment.created_at.desc())

    # Apply filter if provided
    if status_filter:
        query = query.filter_by(status=status_filter.lower())

    shipments = query.all()

    return render_template(
        'admin/all_shipments.html',
        title="All Shipments",
        shipments=shipments,
        status_filter=status_filter
    )



# ASSIGN AGENTS (placeholder)

@adminobj.route('/assign-agents', methods=['GET', 'POST'])
def assign_agents():

    if request.method == "POST":
        shipment_id = request.form.get("shipment_id")
        agent_id = request.form.get("agent_id")

        shipment = Shipment.query.get_or_404(shipment_id)
        agent = Agent.query.get_or_404(agent_id)

        shipment.agent_id = agent.id
        shipment.status = "assigned"
        shipment.assignment_date = datetime.now()
        db.session.commit()

        flash(f"Assigned {agent.full_name} to shipment {shipment.tracking_number}", "success")
        return redirect(url_for("bpadmin.assign_agents"))

    # GET request
    shipments = Shipment.query.order_by(Shipment.created_at.desc()).all()
    agents = Agent.query.filter_by(is_active=True).all()

    return render_template(
        "admin/assign_agents.html",
        shipments=shipments,
        agents=agents
    )

@adminobj.route('/unassign-agent/<int:shipment_id>/')
def unassign_agent(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    shipment.agent_id = None
    shipment.status = "pending"
    db.session.commit()
    flash(f"Unassigned agent from shipment {shipment.tracking_number}", "info")
    return redirect(url_for("bpadmin.assign_agents"))






# USER MANAGEMENT

@adminobj.route('/users/')
def manage_users():
    users = User.query.order_by(User.full_name).all()
    return render_template(
        'admin/manage_users.html',
        users=users,
        title="User Control"
    )

@adminobj.route('/users/delete/<int:user_id>/')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.full_name} deleted successfully.", "success")
    return redirect(url_for('bpadmin.manage_users'))


# SYSTEM STATUS TYPES
@adminobj.route('/system/statuses', methods=['GET', 'POST'])
def system_statuses():
    # Example: manage statuses in the database (you can also hard-code initially)
    if request.method == "POST":
        # Handle adding a new status
        new_status = request.form.get('status_name', '').strip()
        if new_status:
            # Check if already exists
            if StatusType.query.filter_by(name=new_status).first():
                flash("Status already exists.", "warning")
            else:
                st = StatusType(name=new_status)
                db.session.add(st)
                db.session.commit()
                flash("Status added successfully.", "success")
        return redirect(url_for('bpadmin.system_statuses'))

    # GET: show all statuses
    statuses = StatusType.query.order_by(StatusType.name).all()
    return render_template('admin/system_statuses.html', statuses=statuses)


@adminobj.route('/delivery-zones')
def delivery_zones():
    zones = []  # Replace with Zone.query.all()
    return render_template('delivery_zones.html', title="Delivery Zones", zones=zones)

@adminobj.route('/agents/', methods=['GET', 'POST'])
def manage_agents():

    if request.method == "POST":
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        status = request.form.get('status', 'active').strip()
        password = request.form.get('password', '').strip()

        vehicle_type = request.form.get('vehicle_type')
        state = request.form.get('state')
        city = request.form.get('city')

        # basic validation
        if not all([full_name, email, vehicle_type, state, city]):
            flash("All fields including vehicle, state and city are required.", "danger")
            return redirect(url_for('bpadmin.manage_agents'))

        if Agent.query.filter_by(email=email).first():
            flash("An agent with this email already exists.", "danger")
            return redirect(url_for('bpadmin.manage_agents'))

        # password logic
        generated_pw = None
        if not password:
            generated_pw = generate_temp_password(10)
            password = generated_pw

        new_agent = Agent(
            full_name=full_name,
            email=email,
            phone=phone,
            vehicle_type=vehicle_type,
            state=state,
            city=city,
            is_active=(status == 'active'),
            is_available=True
        )
        new_agent.set_password(password)

        db.session.add(new_agent)
        db.session.commit()

        flash(
            f"Agent created. Temporary password: {generated_pw}"
            if generated_pw else "Agent created successfully.",
            "success"
        )

        return redirect(url_for('bpadmin.manage_agents'))

    agents = Agent.query.order_by(Agent.full_name).all()
    return render_template(
        'admin/manage_agents.html',
        agents=agents,
        locations=NIGERIA_LOCATIONS
    )


@adminobj.route('/agents/edit/<int:agent_id>/', methods=['GET', 'POST'])
def edit_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)

    if request.method == "POST":
        agent.full_name = request.form.get('full_name', agent.full_name).strip()
        agent.email = request.form.get('email', agent.email).strip().lower()
        agent.phone = request.form.get('phone', agent.phone).strip()

        agent.vehicle_type = request.form.get('vehicle_type', agent.vehicle_type)
        agent.state = request.form.get('state', agent.state)
        agent.city = request.form.get('city', agent.city)

        status = request.form.get('status', 'active')
        agent.is_active = (status == 'active')

        new_password = request.form.get('password', '').strip()
        if new_password:
            agent.set_password(new_password)

        db.session.commit()
        flash("Agent updated successfully.", "success")
        return redirect(url_for('bpadmin.manage_agents'))

    return render_template(
        'admin/edit_agent.html',
        agent=agent,
        locations=NIGERIA_LOCATIONS
    )


@adminobj.route('/agents/delete/<int:agent_id>/')
def delete_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)

    db.session.delete(agent)
    db.session.commit()

    flash("Agent deleted successfully.", "success")
    return redirect(url_for('bpadmin.manage_agents'))



@adminobj.route('/create/states-cities')
def create_states_cities():
    """
    Admin route to seed Nigerian states and their cities
    """
    for state_name, cities in NIGERIA_LOCATIONS.items():
        # Check if state already exists
        state = State.query.filter_by(name=state_name).first()
        if not state:
            state = State(name=state_name)
            db.session.add(state)
            db.session.flush()  # make state.id available

        # Add cities
        for city_name in cities:
            exists = City.query.filter_by(name=city_name, state_id=state.id).first()
            if not exists:
                db.session.add(City(name=city_name, state_id=state.id))

    db.session.commit()
    return "Nigerian states and cities created successfully!"


@adminobj.route('/admin/setup_rates', methods=['GET', 'POST'])
def setup_rates():
    """Route to initialize or update all required shipping rates."""
    
    # 1. Define all vehicle types and their initial/default values
    # You can adjust these prices as needed.
    rate_defaults = {
        'bike': {'base_price': 1500.00, 'price_per_kg': 50.00, 'distance_multiplier': 1.00},
        'van': {'base_price': 3500.00, 'price_per_kg': 150.00, 'distance_multiplier': 2.50},
        'bus': {'base_price': 6000.00, 'price_per_kg': 250.00, 'distance_multiplier': 4.00},
    }
    
    updated_count = 0
    
    try:
        for rate_type, defaults in rate_defaults.items():
            # Check if rate already exists
            rate = ShippingRate.query.filter_by(rate_type=rate_type).first()
            
            if rate is None:
                # Insert new rate
                rate = ShippingRate(
                    rate_type=rate_type,
                    base_price=defaults['base_price'],
                    price_per_kg=defaults['price_per_kg'],
                    distance_multiplier=defaults['distance_multiplier']
                )
                db.session.add(rate)
                updated_count += 1
            else:
                # If you ever use a POST method here, you would update existing rates:
                # rate.base_price = defaults['base_price'] 
                # ...
                pass # Skipping updates for simplicity on a GET request
                
        db.session.commit()
        
        if updated_count > 0:
            flash(f"SUCCESS: Initial rates for {updated_count} vehicle types inserted. You can now calculate rates.", 'success')
        else:
            flash("Rates already configured. No changes made.", 'info')

    except Exception as e:
        db.session.rollback()
        flash(f"FATAL ERROR setting up rates: {str(e)}", 'danger')

    # Redirect to a safe page after setup
    return redirect(url_for('bpshipment.new_shipment'))

