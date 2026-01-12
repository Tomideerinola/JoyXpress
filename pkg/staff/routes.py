from flask import render_template,flash,redirect,url_for,request,session
from werkzeug.security import generate_password_hash,check_password_hash
from pkg.staff import staffobj
from pkg.models import db, State, City, ShippingRate,Agent, User, Shipment,Payment,ShipmentStatusHistory,Staff,ContactUs,QuoteRequest
from datetime import datetime

from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()


@staffobj.route('/staff/login/', methods=['GET', 'POST'])
def staff_login():
    """
   Staff login route
    """
    if request.method == "POST":
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        staff =Staff.query.filter_by(email=email).first()

        if staff and staff.check_password(password):

            # Check if the staff is active
            if staff.status != "active":
                flash("Your account is inactive. Contact the administrator.", "danger")
                return redirect(url_for('bpstaff.staff_login'))

            # Save login info to session
            session.clear()
            session['staffonline'] = staff.id

            return redirect(url_for('bpstaff.staff_dashboard'))  # replace with your agent dashboard route

        flash("Invalid email or password", "danger")
        return redirect(url_for('bpstaff.agent_login'))

    # GET request: show login form
    return render_template('staff/staff_login.html')



@staffobj.route('/staff/logout/')
def staff_logout():
    session.clear()
    session.pop('staffonline', None)
    return redirect(url_for('bpstaff.staff_login'))



@staffobj.route('/tasks')
def view_all_tasks():

    staff_id = session.get('staffonline')
    if not staff_id:
        flash('Please log in as a Staff', 'danger')
        return redirect(url_for('bpstaff.staff_login'))

    staff = Staff.query.get_or_404(staff_id)

    assigned_requests = QuoteRequest.query.filter_by(assigned_staff_id=staff.id).all()
    contact_assigned_requests= ContactUs.query.filter_by(assigned_staff_id=staff.id).all()
    pending_requests = [r for r in assigned_requests if r.assignment_status == "pending"]
    completed_requests = [r for r in assigned_requests if r.assignment_status == "completed"]
    contact_pending_requests = [r for r in contact_assigned_requests if r.contact_status == "assigned"]
    contact_completed_requests = [r for r in contact_assigned_requests if r.contact_status == "completed"]
    pending_requests_count = QuoteRequest.query.filter(
    QuoteRequest.assigned_staff_id == staff.id,
    QuoteRequest.assignment_status != "completed"
    ).count()

    contact_pending_requests_count = ContactUs.query.filter(
        ContactUs.assigned_staff_id == staff.id,
        ContactUs.contact_status != "completed"
    ).count()
    return render_template(
        'staff/all_task.html',
        staff=staff,
        assigned_requests=assigned_requests,
        pending_requests=pending_requests,
        completed_requests=completed_requests,
        contact_assigned_requests=contact_assigned_requests,
        contact_completed_requests=contact_completed_requests,
        contact_pending_requests=contact_pending_requests,
        pending_requests_count=pending_requests_count,
        contact_pending_requests_count=contact_pending_requests_count

    )


@staffobj.route('/staff/contact/update-request/<int:id>/', methods=['GET', 'POST'])
def staff_update_contact_request(id):
    if 'staffonline' not in session:
        return redirect(url_for('bpstaff.staff_login'))

    staff = Staff.query.get(session['staffonline'])
    request_item = ContactUs.query.get_or_404(id)

    if request_item.assigned_staff_id != staff.id:
        flash("You cannot update this contact request.", "danger")
        return redirect(url_for('bpstaff.staff_dashboard'))

    if request.method == "POST":
        new_status = request.form.get('status')
        if new_status:
            request_item.contact_status = new_status
            db.session.commit()
            flash("Request status updated.", "success")
        return redirect(url_for('bpstaff.view_contact_request'))

    return render_template('staff/staff_contact_update.html', request_item=request_item)



# this is the staff dashboard route 
@staffobj.route('/staff/dashboard/')
def staff_dashboard():
    if 'staffonline' not in session:
        flash('Please log in as Staff to access the dashboard.', 'danger')
        return redirect(url_for('bpstaff.staff_login'))

    staff = Staff.query.get(session['staffonline'])
    assigned_requests = QuoteRequest.query.filter_by(assigned_staff_id=staff.id).all()
    contact_assigned_requests= ContactUs.query.filter_by(assigned_staff_id=staff.id).all()
    pending_requests = [r for r in assigned_requests if r.assignment_status == "pending"]
    completed_requests = [r for r in assigned_requests if r.assignment_status == "completed"]
    contact_pending_requests = [r for r in contact_assigned_requests if r.contact_status == "assigned"]
    contact_completed_requests = [r for r in contact_assigned_requests if r.contact_status == "completed"]
    pending_requests_count = QuoteRequest.query.filter(
    QuoteRequest.assigned_staff_id == staff.id,
    QuoteRequest.assignment_status != "completed"
    ).count()

    contact_pending_requests_count = ContactUs.query.filter(
        ContactUs.assigned_staff_id == staff.id,
        ContactUs.contact_status != "completed"
    ).count()

    return render_template(
        'staff/dashboard.html',
        staff=staff,
        assigned_requests=assigned_requests,
        pending_requests=pending_requests,
        completed_requests=completed_requests,contact_assigned_requests=contact_assigned_requests,
        contact_pending_requests=contact_pending_requests,
        contact_completed_requests=contact_completed_requests,
        pending_requests_count=pending_requests_count,
        contact_pending_requests_count=contact_pending_requests_count
    )


@staffobj.route('/view/contact-requests/')
def view_contact_request():
    if 'staffonline' not in session:
        return redirect(url_for('bpstaff.staff_login'))

    staff = Staff.query.get(session['staffonline'])
    assigned_requests = QuoteRequest.query.filter_by(assigned_staff_id=staff.id).all()
    contact_assigned_requests= ContactUs.query.filter_by(assigned_staff_id=staff.id).all()
    pending_requests = [r for r in assigned_requests if r.assignment_status == "pending"]
    completed_requests = [r for r in assigned_requests if r.assignment_status == "completed"]
    contact_pending_requests = [r for r in contact_assigned_requests if r.contact_status == "assigned"]
    contact_completed_requests = [r for r in contact_assigned_requests if r.contact_status == "completed"]
    pending_requests_count = QuoteRequest.query.filter(
    QuoteRequest.assigned_staff_id == staff.id,
    QuoteRequest.assignment_status != "completed"
    ).count()

    contact_pending_requests_count = ContactUs.query.filter(
        ContactUs.assigned_staff_id == staff.id,
        ContactUs.contact_status != "completed"
    ).count()


    return render_template(
        'staff/view_contact_request.html',
        staff=staff,
        assigned_requests=assigned_requests,
        pending_requests=pending_requests,
        completed_requests=completed_requests,
        contact_assigned_requests=contact_assigned_requests,
        contact_completed_requests=contact_completed_requests,
        contact_pending_requests=contact_pending_requests,
        pending_requests_count=pending_requests_count,
        contact_pending_requests_count=contact_pending_requests_count

    )