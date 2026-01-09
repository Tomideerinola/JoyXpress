# JoyXpress – Logistics & Parcel Delivery Platform

JoyXpress is a **full-stack logistics application** built with **Flask** that allows users to send parcels across cities and states using buses, bikes, and other road-based transport. It features real-time parcel tracking, automated agent assignment, and a clean, scalable backend architecture using **divisional blueprints**.  


##  Features

### User Features
- Sign up, login, and manage profile
- Create shipment requests with pickup and delivery details
- Calculate shipping cost based on **distance and package weight**
- Track shipments in real-time using **tracking IDs**
- View shipment history and status timeline

### Agent Features
- Agent (rider/driver) login and dashboard
- View assigned shipments
- Update shipment status (picked up, in transit, delivered)
- Availability management by city and vehicle type

### Admin Features
- Manage users, agents, and shipments
- Oversee system operations
- Override shipment statuses if necessary

### Payment Features
- Integrated payment system for shipments
- Automatic agent assignment upon successful payment
- Shipment verification and confirmation

---

## Architecture

JoyXpress follows a **modular divisional blueprint structure** in Flask:

JoyXpress  is organized using a modular divisional blueprint structure in Flask. The application is grouped into clearly defined packages, each responsible for a specific domain of the system. Authentication handles access for users, agents, and administrators. User modules manage sender-related actions and services. Agent modules control rider and driver operations. Shipment modules handle parcel creation, tracking, and status management. Payment modules are responsible for payment processing and post-payment workflows. The tracking module provides public access for parcel tracking using tracking IDs. Administrative modules oversee system management and supervision. Templates store the HTML views used across the application, while static files contain CSS, JavaScript, and other assets used for styling and interactivity.


**Models include:**
- User, Agent, Admin  
- Shipment, ShipmentStatusHistory  
- Payment  

The system follows **services.py** separation, ensuring business logic is decoupled from routes.

---

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate  
- **Frontend:** HTML5, CSS3, Bootstrap (or your chosen template)  
- **Database:** mySQL 
- **Version Control:** Git, GitHub  
- **Payments:** Paystack  

---

## ⚡ How It Works

1. **Shipment Creation:** User enters pickup/delivery info and package weight on the homepage.  
2. **Price Calculation:** Frontend calculates shipping cost using distance & weight.  
3. **Sign Up / Login:** If not logged in, shipment details are temporarily saved in session.  
4. **Payment:** Once payment is confirmed, the backend verifies and marks shipment as paid.  
5. **Agent Assignment:** System automatically assigns an available agent in the pickup location.  
6. **Tracking:** Users can track shipments with tracking IDs in real-time, with full status history.  

---

##  Key Learnings / Skills Demonstrated

- Flask **divisional blueprint architecture**  
- Clean separation: **routes → services → models**  
- Session-based **unsaved shipment handling** before login  
- Automated logistics workflow (shipment → payment → agent assignment)  
- Public **shipment tracking system**  
- Git & GitHub workflow, including handling conflicts and push errors  

---

##  Getting Started

1. **Clone the repository:**
```bash
git clone https://github.com/YourUsername/JoyXpress.git
cd JoyXpress
