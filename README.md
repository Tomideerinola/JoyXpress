# Transjoy – Logistics & Parcel Delivery Platform

Transjoy is a **full-stack logistics application** built with **Flask** that allows users to send parcels across cities and states using buses, bikes, and other road-based transport. It features real-time parcel tracking, automated agent assignment, and a clean, scalable backend architecture using **divisional blueprints**.  

This project is designed to demonstrate **advanced Flask skills, modular architecture, and real-world logistics workflows**, making it ideal for your portfolio or a production-ready system.

---

## 🚀 Features

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

## 🏗 Architecture

Transjoy follows a **modular divisional blueprint structure** in Flask:

PKG/
├── auth/ # Authentication (users, agents, admins)
├── users/ # User (sender) actions and services
├── agents/ # Agent (rider/driver) actions and services
├── shipments/ # Shipment management and tracking
├── payments/ # Payment processing and post-payment logic
├── tracking/ # Public shipment tracking
├── admin/ # Admin dashboard and management
├── templates/ # HTML templates
└── static/ # CSS, JS, assets



**Models include:**
- User, Agent, Admin  
- Shipment, ShipmentStatusHistory  
- Payment  

The system follows **services.py** separation, ensuring business logic is decoupled from routes.

---

## 📦 Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate  
- **Frontend:** HTML5, CSS3, Bootstrap (or your chosen template)  
- **Database:** SQLite (development) / PostgreSQL (production-ready)  
- **Version Control:** Git, GitHub  
- **Payments:** Mocked / ready for integration with Paystack or similar  

---

## ⚡ How It Works

1. **Shipment Creation:** User enters pickup/delivery info and package weight on the homepage.  
2. **Price Calculation:** Frontend calculates shipping cost using distance & weight.  
3. **Sign Up / Login:** If not logged in, shipment details are temporarily saved in session.  
4. **Payment:** Once payment is confirmed, the backend verifies and marks shipment as paid.  
5. **Agent Assignment:** System automatically assigns an available agent in the pickup location.  
6. **Tracking:** Users can track shipments with tracking IDs in real-time, with full status history.  

---

## 💡 Key Learnings / Skills Demonstrated

- Flask **divisional blueprint architecture**  
- Clean separation: **routes → services → models**  
- Session-based **unsaved shipment handling** before login  
- Automated logistics workflow (shipment → payment → agent assignment)  
- Public **shipment tracking system**  
- Git & GitHub workflow, including handling conflicts and push errors  

---

## 📂 Getting Started

1. **Clone the repository:**
```bash
git clone https://github.com/YourUsername/transjoy.git
cd transjoy
