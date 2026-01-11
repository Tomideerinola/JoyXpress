from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    shipments = db.relationship('Shipment', backref='user', lazy=True)
    state = db.relationship('State')
    city = db.relationship('City')


class Agent(db.Model):


    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    vehicle_type = db.Column(db.String(50), nullable=False)  # bike, bus
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)

    is_available = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)


    created_at = db.Column(db.DateTime, default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    shipments = db.relationship('Shipment', backref='agent', lazy=True)



class Admin(db.Model):
    admin_id = db.Column(db.Integer(),primary_key=True, autoincrement=True)
    admin_username = db.Column(db.String(100),nullable=False)
    admin_email=db.Column(db.String(100),unique=True, nullable=False)
    last_login = db.Column(db.DateTime(), default=datetime.utcnow)
    admin_pwd = db.Column(db.String(255),nullable=False)
    


class Shipment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=True)

    receiver_name = db.Column(db.String(120), nullable=False)
    receiver_phone = db.Column(db.String(20), nullable=False)

    pickup_address = db.Column(db.Text, nullable=False)
    pickup_city = db.Column(db.String(100), nullable=False)
    pickup_state = db.Column(db.String(100), nullable=False)

    delivery_address = db.Column(db.Text, nullable=False)
    delivery_city = db.Column(db.String(100), nullable=False)
    delivery_state = db.Column(db.String(100), nullable=False)
    assignment_date = db.Column(db.DateTime, nullable=True)

    package_weight = db.Column(db.Float, nullable=False)  # kg
    delivery_type = db.Column(db.String(50), nullable=False)  # bike, bus

    distance_km = db.Column(db.Float, nullable=False)
    calculated_amount = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(50), default='pending')

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


class ShippingRate(db.Model):
    """
    Hardcoded rates for calculation, used instead of a complex Distance model.
    """
    id = db.Column(db.Integer, primary_key=True)
    rate_type = db.Column(db.String(50), unique=True, nullable=False) # e.g., 'bike', 'bus'
    base_price = db.Column(db.Float, nullable=False) # Fixed starting price
    price_per_kg = db.Column(db.Float, nullable=False) # Price multiplier for weight
    # Placeholder for distance multiplier, used for inter-city charges
    distance_multiplier = db.Column(db.Float, nullable=False)



class Payment(db.Model):


    id = db.Column(db.Integer, primary_key=True)

    shipment_id = db.Column(db.Integer,db.ForeignKey('shipment.id'),nullable=False,unique=True)

    amount = db.Column(db.Float, nullable=False)
    payment_reference = db.Column(db.String(100), unique=True, nullable=False)

    status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    paid_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=db.func.now())

    shipment = db.relationship('Shipment', backref=db.backref('payment', uselist=False))


class ShipmentStatusHistory(db.Model):


    id = db.Column(db.Integer, primary_key=True)

    shipment_id = db.Column(db.Integer,db.ForeignKey('shipment.id'),nullable=False)

    status = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(150))
    note = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=db.func.now())

    shipment = db.relationship('Shipment', backref='status_history')



class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    cities = db.relationship('City', backref='state', lazy=True)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)



