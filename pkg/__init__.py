from flask import Flask,session
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv 
import os 

csrf = CSRFProtect()
load_dotenv()

def create_app():
    from pkg import config
    from pkg.models import db,User,Admin,Agent,Staff #we want app to be aware of db 
    #bring in the instances of the Blueprint 
    from pkg.admin import adminobj
    from pkg.user import userobj
    from pkg.api import apiobj
    from pkg.agent import agentobj
    from pkg.auth import authobj
    from pkg.payments import paymentobj
    from pkg.tracking import trackingobj
    from pkg.shipment import shipmentobj
    from pkg.staff import staffobj

     #create the Flask app instance
     #instance_relative_config=True means config file is relative to instance folder

    app = Flask(__name__,instance_relative_config=True)

    #register the Blueprint so that app can become aware of them and this comes after app, if app is not created we should not use it 
    app.register_blueprint(userobj)
    app.register_blueprint(adminobj)
    app.register_blueprint(apiobj)
    app.register_blueprint(agentobj)
    app.register_blueprint(authobj)
    app.register_blueprint(paymentobj)
    app.register_blueprint(shipmentobj)
    app.register_blueprint(trackingobj)
    app.register_blueprint(staffobj)

    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") # Reads from .env
    app.config['PAYSTACK_SECRET_KEY'] = os.environ.get("PAYSTACK_SECRET_KEY") # Reads from .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", False) # Reads from .env or defaults to False
    
    app.config.from_pyfile('config.py',silent=True)
    app.config.from_object(config.TestConfig)
    csrf.init_app(app) #lazy-loading
    csrf.exempt(apiobj) #API allow visitation to the routes from any source
    db.init_app(app) #lazy-loading i.e suppling app to SQLALchemy class at a later time
    Migrate(app,db)

    @app.context_processor
    def inject_logged_in_accounts():
        user = None
        agent = None
        admin = None
        staff = None

        if session.get('useronline'):
            user = User.query.get(session['useronline'])

        if session.get('agentonline'):
            agent = Agent.query.get(session['agentonline'])

        if session.get('adminonline'):
            admin = Admin.query.get(session['adminonline'])

        if session.get('staffonline'):
            staff = Staff.query.get(session['staffonline'])

        return dict(
            user=user,
            agent=agent,
            admin=admin,
            staff=staff
        )
    
    return app


app = create_app()


from pkg import models,general_routes
#, models  # Import routes and models to ensure they are loaded and the app recognizes them