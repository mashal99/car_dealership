import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.models import db, Customer, Vehicle, ServiceAppointment, SalesStats
from datetime import datetime

# Initialize the logger
logging.basicConfig(
    filename='app_logs.log',  # Log file
    level=logging.INFO,       # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET'])
def home():
    """Default homepage."""
    logging.info("Accessed homepage.")
    return render_template('home.html')

# --- Customer API Routes ---
@bp.route('/customers', methods=['POST'])
def add_customer():
    """Add a new customer."""
    try:
        data = request.form
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(customer)
        db.session.commit()
        logging.info(f"Customer added: {customer.first_name} {customer.last_name}")
        return jsonify({"message": "Customer added successfully!"}), 201
    except Exception as e:
        logging.error(f"Error adding customer: {e}")
        return jsonify({"error": str(e)}), 400

# --- Customer Page Routes ---
@bp.route('/add_customer', methods=['GET', 'POST'])
def handle_add_customer():
    """Add a customer via a web form."""
    if request.method == 'POST':
        try:
            # Retrieve form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            address = request.form.get('address')

            # Generate a unique customer_id
            max_id = db.session.query(db.func.max(Customer.customer_id)).scalar() or 0
            customer_id = max_id + 1

            # Create and add customer
            customer = Customer(
                customer_id=customer_id,  # Explicitly set customer_id
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
            logging.info(f"Customer added via form: {first_name} {last_name} (ID: {customer_id})")
            flash("Customer added successfully!", "success")
            return redirect('/add_customer')
        except Exception as e:
            logging.error(f"Error adding customer via form: {e}")
            flash("An error occurred while adding the customer.", "danger")
    return render_template('add_customer.html')



@bp.route('/schedule_service', methods=['GET', 'POST'])
def schedule_service_page():
    """Display and handle the service scheduling page."""
    if request.method == 'POST':
        try:
            data = request.form
            appointment = ServiceAppointment(
                appt_date=data['appt_date'],
                arrival_time=data['arrival_time'],
                service_customer_id=data['service_customer_id'],
                vehicle_serviced_id=data['vehicle_serviced_id'],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(appointment)
            db.session.commit()
            logging.info(f"Service scheduled for Customer ID: {data['service_customer_id']}")
            flash("Service appointment scheduled successfully!", "success")
            return redirect('/schedule_service')
        except Exception as e:
            logging.error(f"Error scheduling service: {e}")
            flash("An error occurred while scheduling the service.", "danger")
    return render_template('schedule_service.html')

@bp.route('/sell_car', methods=['POST'])
def sell_car():
    """Handle the sale of a car."""
    try:
        data = request.json
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            logging.warning(f"Vehicle not found: {data['vehicle_id']}")
            return jsonify({"error": "Vehicle not found"}), 404

        vehicle.sold_at = datetime.strptime(data['sold_at'], '%Y-%m-%d').date()
        vehicle.sale_price = data['sale_price']
        vehicle.profit = vehicle.sale_price - vehicle.purchase_price

        customer = Customer.query.get(data['customer_id'])
        if not customer:
            logging.warning(f"Customer not found: {data['customer_id']}")
            return jsonify({"error": "Customer not found"}), 404

        customer.total_spent = (customer.total_spent or 0) + vehicle.sale_price
        customer.total_profit = (customer.total_profit or 0) + vehicle.profit

        db.session.commit()
        logging.info(f"Car sold: Vehicle ID {data['vehicle_id']} to Customer ID {data['customer_id']}")
        return jsonify({"message": "Car sale recorded successfully!"}), 201
    except Exception as e:
        logging.error(f"Error selling car: {e}")
        return jsonify({"error": str(e)}), 400

@bp.route('/complete_service/<int:appt_id>', methods=['POST'])
def complete_service(appt_id):
    """Complete a service appointment and record total cost."""
    try:
        data = request.json
        appointment = ServiceAppointment.query.get(appt_id)
        if not appointment:
            logging.warning(f"Appointment not found: {appt_id}")
            return jsonify({"error": "Appointment not found"}), 404

        appointment.completion_time = datetime.strptime(data['completion_time'], '%H:%M').time()
        appointment.total_cost = data['labor_cost'] + sum(data['parts_costs'])
        db.session.commit()
        logging.info(f"Service completed: Appointment ID {appt_id}")
        return jsonify({"message": "Service appointment completed successfully!"})
    except Exception as e:
        logging.error(f"Error completing service: {e}")
        return jsonify({"error": str(e)}), 400

@bp.route('/sales_statistics', methods=['POST'])
def get_sales_statistics():
    """Retrieve sales statistics for a specific period."""
    try:
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
        logging.info(f"Sales statistics retrieved for period: {start_date} to {end_date}")
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error retrieving sales statistics: {e}")
        return jsonify({"error": str(e)}), 400

@bp.route('/bill/<int:sale_id>', methods=['GET'])
def generate_bill(sale_id):
    """Generate a bill for a car sale."""
    try:
        sale = Sale.query.get(sale_id)
        if not sale:
            logging.warning(f"Sale not found: {sale_id}")
            return "Sale not found", 404
        customer = sale.customer
        vehicle = sale.car
        logging.info(f"Bill generated for Sale ID: {sale_id}")
        return render_template('bill.html', sale=sale, customer=customer, vehicle=vehicle)
    except Exception as e:
        logging.error(f"Error generating bill: {e}")
        return "An error occurred while generating the bill.", 500

@bp.route('/vehicles', methods=['POST'])
def add_vehicle():
    """Add a new vehicle via API."""
    try:
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
        logging.info(f"Vehicle added: {vehicle.make} {vehicle.model} (ID: {vehicle.vehicle_id})")
        return jsonify({"message": "Vehicle added successfully!"}), 201
    except Exception as e:
        logging.error(f"Error adding vehicle: {e}")
        return jsonify({"error": str(e)}), 400

@bp.route('/sales_statistics', methods=['GET'])
def sales_statistics_page():
    """Render the Sales Statistics page."""
    try:
        stats = db.session.query(
            Vehicle.make, Vehicle.model, db.func.sum(SalesStats.cars_sold), db.func.sum(SalesStats.total_profit)
        ).join(SalesStats).group_by(Vehicle.make, Vehicle.model).all()

        formatted_stats = [
            {"make": row[0], "model": row[1], "cars_sold": row[2], "total_profit": row[3]}
            for row in stats
        ]
        logging.info("Sales statistics page accessed.")
        return render_template('sales_statistics.html', stats=formatted_stats)
    except Exception as e:
        logging.error(f"Error rendering sales statistics page: {e}")
        return "An error occurred while loading the page.", 500