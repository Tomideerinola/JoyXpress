from flask import render_template,flash,redirect,url_for,request,session
from werkzeug.security import generate_password_hash,check_password_hash
from pkg.agent import agentobj
from pkg.models import db, State, City, ShippingRate,Agent, User, Shipment,Payment,ShipmentStatusHistory

from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@agentobj.route('/agent/login/', methods=['GET', 'POST'])
def agent_login():
    """
    Agent login route
    """
    if request.method == "POST":
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        agent = Agent.query.filter_by(email=email).first()

        if agent and agent.check_password(password):

            # Check if the agent is active
            if not agent.is_active:
                flash("Your account is inactive. Contact the administrator.", "danger")
                return redirect(url_for('bpadmin.agent_login'))

            # Save login info to session
            session.clear()
            session['agentonline'] = agent.id

            return redirect(url_for('bpagent.agent_dashboard'))  # replace with your agent dashboard route

        flash("Invalid email or password", "danger")
        return redirect(url_for('bpadmin.agent_login'))

    # GET request: show login form
    return render_template('agent/agent_login.html')


@agentobj.route('/agent/logout/', methods=['POST', 'GET'])
def agent_logout():
    if session.get('agentonline')!=None:
        session.pop('agentonline')   
    return redirect(url_for("bpagent.agent_login"))


@agentobj.route('/dashboard')
def agent_dashboard():
    # Get the logged-in agent from session
    agent_id = session.get('agentonline')
    if not agent_id:
        return redirect(url_for('bpagent.login'))

    agent = Agent.query.get(agent_id)
    if not agent:
        session.pop('agent_id', None)
        return redirect(url_for('bpagent.login'))

    # Save agent online session info
    session['agentonline'] = {
        'id': agent.id,
        'full_name': agent.full_name,
        'email': agent.email,
        'is_active': agent.is_active
    }

    # Fetch shipments assigned to this agent
    total_shipments = Shipment.query.filter_by(agent_id=agent.id).count()
    active_shipments = Shipment.query.filter(
        Shipment.agent_id == agent.id,
        Shipment.status.in_(["Pending", "In Transit"])
    ).count()

    shipments = Shipment.query.filter_by(agent_id=agent.id).order_by(Shipment.created_at.desc()).all()

    return render_template(
        'agent/agent_dashboard.html',
        agent=agent,
        total_shipments=total_shipments,
        active_shipments=active_shipments,
        shipments=shipments
    )
