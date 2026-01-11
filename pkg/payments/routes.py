# pkg/payments/routes.py

from flask import Blueprint, session, flash, redirect, url_for, request, current_app, render_template
import requests,uuid
import json
from . import paymentobj 
from pkg.models import db, Shipment,Payment # Import Shipment and db
from datetime import datetime
from pkg.payments.services import verify_paystack_transaction



@paymentobj.route('/initiate/<int:shipment_id>')
def initiate_payment(shipment_id):

    user_id = session.get('useronline')
    if not user_id:
        flash('Please login to continue.', 'warning')
        return redirect(url_for('bpuser.login'))

    shipment = Shipment.query.get_or_404(shipment_id)

    if shipment.user_id != user_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('bpuser.dashboard'))

    if shipment.status != 'pending':
        flash('Shipment already paid or processed.', 'info')
        return redirect(url_for('bpuser.dashboard'))

    # ✅ Check for existing payment
    payment = Payment.query.filter_by(shipment_id=shipment.id).first()

    if not payment:
        payment = Payment(
            shipment_id=shipment.id,
            amount=shipment.calculated_amount,
            payment_reference=f"JX-{shipment.tracking_number}",
            status='pending'
        )
        db.session.add(payment)
        db.session.commit()

    secret_key = current_app.config['PAYSTACK_SECRET_KEY']

    payload = {
        "email": shipment.user.email,
        "amount": int(payment.amount * 100),
        "reference": payment.payment_reference,
        "callback_url": url_for('bppayment.verify_payment', _external=True)
    }

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        headers=headers,
        json=payload
    )

    res = response.json()

    if not res.get('status'):
        flash('Unable to initialize payment.', 'danger')
        return redirect(url_for('bpshipment.confirmation', shipment_id=shipment.id))

    return redirect(res['data']['authorization_url'])

@paymentobj.route('/verify')
def verify_payment():

    reference = request.args.get('reference')
    if not reference:
        flash('Missing payment reference.', 'danger')
        return redirect(url_for('bpuser.dashboard'))

    payment = Payment.query.filter_by(payment_reference=reference).first()
    if not payment:
        flash('Invalid payment reference.', 'danger')
        return redirect(url_for('bpuser.dashboard'))

    success, data = verify_paystack_transaction(reference)

    if success:
        payment.status = 'paid'
        payment.paid_at = datetime.utcnow()

        shipment = payment.shipment
        shipment.status = 'paid'

        db.session.commit()

        flash('Payment successful!', 'success')
        return redirect(url_for(
            'bppayment.payment_success',
            shipment_id=shipment.id
        ))

    else:
        payment.status = 'failed'
        db.session.commit()

        flash('Payment failed. Please try again.', 'danger')
        return redirect(url_for(
            'bpshipment.confirmation',
            shipment_id=payment.shipment_id
        ))

@paymentobj.route('/success/<int:shipment_id>')
def payment_success(shipment_id):
    user_id = session.get('useronline')
    shipment = Shipment.query.get_or_404(shipment_id)
    shipments = Shipment.query.filter_by(user_id=user_id).order_by(Shipment.created_at.desc()).all()


    if shipment.status != 'paid':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('bpuser.dashboard'))

    return render_template(
        'payments/success.html',
        shipment=shipment,shipments=shipments
    )
