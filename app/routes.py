import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.models import db, Customer, Vehicle, ServiceAppointment, SalesStats
from datetime import datetime

# Initialize the logger
logging.basicConfig(
    filename='app_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET'])
def home():
    """Default homepage."""
    logging.info("Accessed homepage.")
    return render_template('home.html')

from decimal import Decimal

from decimal import Decimal
from sqlalchemy.sql import func

@bp.route('/sell_car', methods=['GET', 'POST'])
def sell_car():
    """Handle car sale and render the form."""
    if request.method == 'GET':
        logging.info("Accessed Sell Car page.")
        return render_template('sell_car.html')

    if request.method == 'POST':
        try:
            # Extract form data
            data = request.form
            vehicle_id = data.get('vehicle_id')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            sale_price = float(data.get('sale_price'))
            sold_at = data.get('sold_at')

            # Validate input
            if not all([vehicle_id, first_name, last_name, sale_price, sold_at]):
                logging.error("Missing form fields for car sale.")
                flash("All fields are required.", "danger")
                return redirect('/sell_car')

            # Check if the vehicle exists
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                logging.warning(f"Vehicle not found: {vehicle_id}")
                flash("Vehicle not found.", "danger")
                return redirect('/sell_car')

            # Check if the customer exists
            customer = Customer.query.filter_by(first_name=first_name, last_name=last_name).first()
            if not customer:
                # If customer doesn't exist, create a new customer
                max_id = db.session.query(func.max(Customer.customer_id)).scalar() or 0
                customer_id = max_id + 1
                customer = Customer(
                    customer_id=customer_id,
                    first_name=first_name,
                    last_name=last_name,
                    total_spent=Decimal(0),
                    total_profit=Decimal(0),
                    created_at=datetime.now().date(),
                    updated_at=datetime.now().date(),
                )
                db.session.add(customer)
                db.session.commit()
                logging.info(f"New customer added: {first_name} {last_name} (ID: {customer_id})")
            else:
                customer_id = customer.customer_id

            # Update vehicle details
            vehicle.sold_at = datetime.strptime(sold_at, '%Y-%m-%d').date()
            vehicle.sale_price = sale_price
            vehicle.profit = Decimal(sale_price) - Decimal(vehicle.purchase_price)
            vehicle.owner_id = customer_id

            # Update customer details
            customer.total_spent += Decimal(sale_price)
            customer.total_profit += vehicle.profit

            # Update/Add sales stats
            stats = db.session.query(SalesStats).filter(
                SalesStats.vehicle_stat_id == vehicle_id
            ).first()

            if stats:
                # Update existing stats record
                stats.cars_sold += 1
                stats.total_profit += vehicle.profit
                stats.end_date = vehicle.sold_at
            else:
                # Create new stats record
                stats = SalesStats(
                    vehicle_stat_id=vehicle_id,
                    start_date=vehicle.sold_at,
                    end_date=vehicle.sold_at,
                    cars_sold=1,
                    total_profit=vehicle.profit,
                    created_at=datetime.now(),
                )
                db.session.add(stats)

            db.session.commit()
            logging.info(
                f"Car sold: Vehicle ID {vehicle_id} to Customer ID {customer_id}. Stats updated."
            )
            flash("Car sale recorded successfully!", "success")
            return redirect('/sell_car')
        except Exception as e:
            logging.error(f"Error in car sale: {e}")
            flash("An error occurred during the car sale process.", "danger")
            return redirect('/sell_car')


@bp.route('/bill/<int:vehicle_id>', methods=['GET'])
def generate_bill(vehicle_id):
    """Generate and display the bill for a car sale."""
    try:
        # Fetch the vehicle details
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            logging.warning(f"Vehicle not found: {vehicle_id}")
            flash("Vehicle not found.", "danger")
            return redirect('/sell_car')

        # Fetch the customer details
        customer = Customer.query.get(vehicle.owner_id)
        if not customer:
            logging.warning(f"Customer not found for Vehicle ID: {vehicle_id}")
            flash("Customer not found.", "danger")
            return redirect('/sell_car')

        # Prepare data for the bill
        bill_data = {
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "customer_phone": customer.phone,
            "customer_email": customer.email,
            "vehicle_make": vehicle.make,
            "vehicle_model": vehicle.model,
            "vehicle_year": vehicle.year,
            "vehicle_vin": vehicle.vin,
            "sale_price": f"${vehicle.sale_price:.2f}",
            "sale_date": vehicle.sold_at.strftime('%Y-%m-%d') if vehicle.sold_at else "N/A",
            "profit": f"${vehicle.profit:.2f}",
        }

        logging.info(f"Bill generated for Vehicle ID: {vehicle_id}")
        return render_template('bill.html', bill_data=bill_data)

    except Exception as e:
        logging.error(f"Error generating bill: {e}")
        flash("An error occurred while generating the bill.", "danger")
        return redirect('/sell_car')


@bp.route('/schedule_service', methods=['GET', 'POST'])
def schedule_service_page():
    """Handle service scheduling."""
    if request.method == 'POST':
        try:
            data = request.form
            appointment = ServiceAppointment(
                appt_date=datetime.strptime(data['appt_date'], '%Y-%m-%d').date(),
                arrival_time=datetime.strptime(data['arrival_time'], '%H:%M').time(),
                service_customer_id=int(data['service_customer_id']),
                vehicle_serviced_id=int(data['vehicle_serviced_id']),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(appointment)
            db.session.commit()
            logging.info(f"Service scheduled for Customer ID: {data['service_customer_id']}")
            flash("Service appointment scheduled successfully!", "success")
        except Exception as e:
            logging.error(f"Error scheduling service: {e}")
            flash("An error occurred while scheduling the service.", "danger")
    return render_template('schedule_service.html')

@bp.route('/sales_statistics', methods=['GET', 'POST'])
def sales_statistics_page():
    """Retrieve and display sales statistics."""
    if request.method == 'POST':
        try:
            data = request.form
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
            return render_template('sales_statistics.html', stats=results)
        except Exception as e:
            logging.error(f"Error retrieving sales statistics: {e}")
            flash("An error occurred while retrieving sales statistics.", "danger")
    return render_template('sales_statistics.html')

@bp.route('/add_customer', methods=['GET', 'POST'])
def handle_add_customer():
    """Add a customer via a web form."""
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            address = request.form.get('address')

            max_id = db.session.query(db.func.max(Customer.customer_id)).scalar() or 0
            customer_id = max_id + 1

            customer = Customer(
                customer_id=customer_id,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                address=address,
                total_spent=0.0,
                total_profit=0.0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(customer)
            db.session.commit()
            logging.info(f"Customer added: {first_name} {last_name} (ID: {customer_id})")
            flash("Customer added successfully!", "success")
        except Exception as e:
            logging.error(f"Error adding customer: {e}")
            flash("An error occurred while adding the customer.", "danger")
    return render_template('add_customer.html')
