from flask import Blueprint, request, jsonify
from app.models import db, Customer, Vehicle, ServiceAppointment, ServicePackage, SalesStats
from datetime import datetime

bp = Blueprint('routes', __name__)

# --- Customer Routes ---
@bp.route('/customers', methods=['POST'])
def add_customer():
    """Add a new customer."""
    data = request.json
    customer = Customer(
        customer_id=data['customer_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data['phone'],
        email=data['email'],
        address=data['address'],
        total_spent=data['total_spent'],
        total_profit=data['total_profit'],
        created_at=data['created_at'],
        updated_at=data['updated_at']
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({"message": "Customer added successfully!"}), 201

# --- Vehicle Routes ---
@bp.route('/vehicles', methods=['POST'])
def add_vehicle():
    """Add a new vehicle."""
    data = request.json
    vehicle = Vehicle(
        vehicle_id=data['vehicle_id'],
        make=data['make'],
        model=data['model'],
        year=data['year'],
        vin=data['vin'],
        purchase_price=data['purchase_price'],
        sale_price=data['sale_price'],
        profit=data['profit'],
        owner_id=data['owner_id'],
        sold_at=data['sold_at'],
        created_at=data['created_at'],
        updated_at=data['updated_at']
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle added successfully!"}), 201

# --- Service Appointment Routes ---
@bp.route('/appointments', methods=['POST'])
def add_service_appointment():
    """Add a service appointment."""
    data = request.json
    appointment = ServiceAppointment(
        appt_id=data['appt_id'],
        appt_date=data['appt_date'],
        arrival_time=data['arrival_time'],
        completion_time=data['completion_time'],
        service_customer_id=data['service_customer_id'],
        vehicle_serviced_id=data['vehicle_serviced_id'],
        created_at=data['created_at'],
        updated_at=data['updated_at']
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({"message": "Service appointment added successfully!"}), 201

# --- Sales Statistics Routes ---
@bp.route('/sales_stats', methods=['GET'])
def get_sales_stats():
    """Retrieve sales statistics."""
    stats = db.session.query(
        Vehicle.make, Vehicle.model, db.func.sum(SalesStats.cars_sold), db.func.sum(SalesStats.total_profit)
    ).join(SalesStats).group_by(Vehicle.make, Vehicle.model).all()

    results = [
        {"make": row[0], "model": row[1], "cars_sold": row[2], "total_profit": row[3]}
        for row in stats
    ]
    return jsonify(results)
