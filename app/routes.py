from flask import Blueprint, request, jsonify, render_template
from app.models import db, Customer, Vehicle, ServiceAppointment, SalesStats
from datetime import datetime

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET'])
def home():
    """Default homepage."""
    return render_template('home.html')


# --- Customer API Routes ---
@bp.route('/customers', methods=['POST'])
def add_customer():
    """Add a new customer via API."""
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

# --- Customer Page Routes ---
@bp.route('/add_customer', methods=['GET', 'POST'])
def handle_add_customer():
    """Add a customer via a web form."""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')

        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            address=address,
            total_spent=0.0,
            total_profit=0.0,
            created_at=datetime.now().date(),
            updated_at=datetime.now().date()
        )
        db.session.add(customer)
        db.session.commit()
        return render_template('add_customer.html', message="Customer added successfully!")
    return render_template('add_customer.html')

@bp.route('/sell_car', methods=['POST'])
def sell_car():
    """Handle the sale of a car."""
    data = request.json
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    # Update vehicle data
    vehicle.sold_at = datetime.strptime(data['sold_at'], '%Y-%m-%d').date()
    vehicle.sale_price = data['sale_price']
    vehicle.profit = vehicle.sale_price - vehicle.purchase_price

    # Update customer data
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    customer.total_spent = (customer.total_spent or 0) + vehicle.sale_price
    customer.total_profit = (customer.total_profit or 0) + vehicle.profit

    db.session.commit()
    return jsonify({"message": "Car sale recorded successfully!"}), 201

@bp.route('/complete_service/<int:appt_id>', methods=['POST'])
def complete_service(appt_id):
    """Complete a service appointment and record total cost."""
    data = request.json
    appointment = ServiceAppointment.query.get(appt_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    appointment.completion_time = datetime.strptime(data['completion_time'], '%H:%M').time()
    appointment.total_cost = data['labor_cost'] + sum(data['parts_costs'])
    db.session.commit()
    return jsonify({"message": "Service appointment completed successfully!"})

@bp.route('/sales_statistics', methods=['POST'])
def get_sales_statistics():
    """Retrieve sales statistics for a specific period."""
    data = request.json
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

    stats = db.session.query(
        Vehicle.make, Vehicle.model, db.func.count(Vehicle.vehicle_id), db.func.sum(Vehicle.profit)
    ).filter(Vehicle.sold_at.between(start_date, end_date)).group_by(Vehicle.make, Vehicle.model).all()

    results = [
        {"make": row[0], "model": row[1], "cars_sold": row[2], "total_profit": row[3]}
        for row in stats
    ]
    return jsonify(results)


@bp.route('/bill/<int:sale_id>', methods=['GET'])
def generate_bill(sale_id):
    """Generate a bill for a car sale."""
    sale = Sale.query.get(sale_id)
    if not sale:
        return "Sale not found", 404
    customer = sale.customer
    vehicle = sale.car
    return render_template('bill.html', sale=sale, customer=customer, vehicle=vehicle)


# --- Vehicle Routes ---
@bp.route('/vehicles', methods=['POST'])
def add_vehicle():
    """Add a new vehicle via API."""
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

# --- Sales Statistics Page Route ---
@bp.route('/sales_statistics', methods=['GET'])
def sales_statistics_page():
    """Render the Sales Statistics page."""
    stats = db.session.query(
        Vehicle.make, Vehicle.model, db.func.sum(SalesStats.cars_sold), db.func.sum(SalesStats.total_profit)
    ).join(SalesStats).group_by(Vehicle.make, Vehicle.model).all()

    formatted_stats = [
        {"make": row[0], "model": row[1], "cars_sold": row[2], "total_profit": row[3]}
        for row in stats
    ]
    return render_template('sales_statistics.html', stats=formatted_stats)
