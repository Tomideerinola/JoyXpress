from flask import render_template,flash,redirect,url_for,request,session
from werkzeug.security import generate_password_hash,check_password_hash
from pkg.agent import agentobj
from pkg.models import db, State, City, ShippingRate,Agent, User, Shipment,Payment,ShipmentStatusHistory
from datetime import datetime

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
        return redirect(url_for('bpagent.agent_login'))

    # GET request: show login form
    return render_template('agent/agent_login.html')


@agentobj.route('/agent/logout/', methods=['POST', 'GET'])
def agent_logout():
    if session.get('agentonline')!=None:
        session.pop('agentonline')   
    return redirect(url_for("bpagent.agent_login"))



@agentobj.route('/dashboard')
def agent_dashboard():

    # 1️⃣ Enforce agent login
    agent_id = session.get('agentonline')
    if not agent_id:
        flash('Please log in as an agent', 'danger')
        return redirect(url_for('bpagent.agent_login'))

    agent = Agent.query.get(agent_id)
    if not agent:
        session.pop('agentonline', None)
        flash('Session expired. Please log in again.', 'danger')
        return redirect(url_for('bpagent.login'))

    # 2️⃣ Fetch assigned shipments
    assigned_shipments = (
        Shipment.query
        .filter_by(agent_id=agent.id)
        .order_by(Shipment.created_at.desc())
        .all()
    )

    # 3️⃣ Dashboard stats
    total_assignments = len(assigned_shipments)

    active_assignments = (
        Shipment.query
        .filter_by(agent_id=agent.id)
        .filter(Shipment.status.in_(['Assigned', 'Picked Up', 'In Transit']))
        .count()
    )

    completed_assignments = (
        Shipment.query
        .filter_by(agent_id=agent.id, status='Delivered')
        .count()
    )

    return render_template(
        'agent/agent_dashboard.html',
        agent=agent,
        total_assignments=total_assignments,
        active_assignments=active_assignments,
        completed_assignments=completed_assignments,
        assigned_shipments=assigned_shipments,
        today=datetime.now()
    )



@agentobj.route('/shipment/<int:shipment_id>/update-status', methods=['POST'])
def update_shipment_status(shipment_id):

    agent_id = session.get('agentonline')
    if not agent_id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('bpagent.login'))

    shipment = Shipment.query.get_or_404(shipment_id)

    # Security check: agent can only update THEIR shipment
    if shipment.agent_id != agent_id:
        flash('You are not allowed to update this shipment', 'danger')
        return redirect(url_for('bpagent.agent_dashboard'))

    new_status = request.form.get('new_status')
    allowed_statuses = ['Picked Up', 'In Transit', 'Delivered']

    if new_status not in allowed_statuses:
        flash('Invalid status update', 'danger')
        return redirect(url_for('bpagent.agent_dashboard'))

    shipment.status = new_status

    if new_status == 'Delivered':
        shipment.delivered_at = datetime.utcnow()

    db.session.commit()

    flash(f'Shipment marked as {new_status}', 'success')
    return redirect(url_for('bpagent.agent_dashboard'))




@agentobj.route('/tasks')
def view_all_tasks():

    agent_id = session.get('agentonline')
    if not agent_id:
        flash('Please log in as an agent', 'danger')
        return redirect(url_for('bpagent.agent_login'))

    agent = Agent.query.get_or_404(agent_id)

    shipments = (
        Shipment.query
        .filter_by(agent_id=agent.id)
        .order_by(Shipment.created_at.desc())
        .all()
    )

    return render_template(
        'agent/all_tasks.html',
        agent=agent,
        shipments=shipments,
        today=datetime.now()
    )