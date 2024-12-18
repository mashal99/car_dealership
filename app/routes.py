import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, send_file
from app.models import db, Customer, Vehicle, ServiceAppointment, SalesStats, ServicePackage
from datetime import datetime
from reportlab.pdfgen import canvas
import os
import tempfile

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
            # Update customer details
            customer.total_spent = (customer.total_spent or Decimal(0)) + Decimal(sale_price)
            customer.total_profit = (customer.total_profit or Decimal(0)) + vehicle.profit


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
            # Redirect to bill page
            return redirect(url_for('routes.generate_bill', vehicle_id=vehicle.vehicle_id))
    
        except Exception as e:
            logging.error(f"Error in car sale: {e}")
            flash("An error occurred during the car sale process.", "danger")
            return redirect('/sell_car')

@bp.route('/bill/<int:vehicle_id>', methods=['GET'])
def generate_bill(vehicle_id):
    """Generate and display or download the bill."""
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
            "customer_phone": customer.phone or "N/A",
            "customer_email": customer.email or "N/A",
            "vehicle_make": vehicle.make,
            "vehicle_model": vehicle.model,
            "vehicle_year": vehicle.year,
            "vehicle_vin": vehicle.vin,
            "sale_price": f"${vehicle.sale_price:.2f}" if vehicle.sale_price else "N/A",
            "sale_date": vehicle.sold_at.strftime('%Y-%m-%d') if vehicle.sold_at else "N/A",
            "profit": f"${vehicle.profit:.2f}" if vehicle.profit else "N/A",
        }

        # Generate the PDF using ReportLab
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf_file = tmp_file.name
            c = canvas.Canvas(pdf_file)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, 800, "Car Dealership Bill")
            c.setFont("Helvetica", 12)
            c.drawString(100, 770, f"Customer Name: {bill_data['customer_name']}")
            c.drawString(100, 750, f"Phone: {bill_data['customer_phone']}")
            c.drawString(100, 730, f"Email: {bill_data['customer_email']}")
            c.drawString(100, 710, f"Vehicle: {bill_data['vehicle_make']} {bill_data['vehicle_model']} ({bill_data['vehicle_year']})")
            c.drawString(100, 690, f"VIN: {bill_data['vehicle_vin']}")
            c.drawString(100, 670, f"Sale Price: {bill_data['sale_price']}")
            c.drawString(100, 650, f"Sale Date: {bill_data['sale_date']}")
            c.drawString(100, 630, f"Profit: {bill_data['profit']}")
            c.drawString(100, 600, "Thank you for your business!")
            c.save()

        # Serve the PDF as a downloadable file
        return send_file(
            pdf_file,
            as_attachment=True,
            download_name=f"bill_{vehicle_id}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        logging.error(f"Error generating bill: {e}")
        flash("An error occurred while generating the bill.", "danger")
        return redirect('/sell_car')
    finally:
        # Cleanup: Remove the generated PDF file after it is served
        if 'pdf_file' in locals() and os.path.exists(pdf_file):
            os.remove(pdf_file)


    
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

@bp.route('/service', methods=['GET', 'POST'])
def schedule_service():
    """Handle scheduling a service appointment."""
    if request.method == 'GET':
        logging.info("Accessed Service Scheduling page.")
        service_packages = ServicePackage.query.all()
        return render_template('schedule_service.html', service_packages=service_packages)


    if request.method == 'POST':
        try:
            # Extract form data
            data = request.form
            service_package_id = data.get('service_package_id')
            vehicle_id = data.get('vehicle_id')
            appt_date = data.get('appt_date')
            arrival_time = data.get('arrival_time')

            # Validate form inputs
            if not all([service_package_id, vehicle_id, appt_date, arrival_time]):
                logging.error("Missing required form fields for scheduling a service.")
                flash("All fields are required.", "danger")
                return redirect('/service')

            # Validate service package
            service_package = ServicePackage.query.get(service_package_id)
            if not service_package:
                logging.warning(f"Service package not found: {service_package_id}")
                flash("Invalid service package selected.", "danger")
                return redirect('/service')

            # Validate vehicle
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                logging.error(f"Invalid vehicle ID: {vehicle_id}")
                flash("Invalid vehicle ID.", "danger")
                return redirect('/service')

            # Schedule the service
            appointment = ServiceAppointment(
                appt_date=datetime.strptime(appt_date, '%Y-%m-%d').date(),
                arrival_time=datetime.strptime(arrival_time, '%H:%M').time(),
                service_customer_id=vehicle.owner_id,
                vehicle_serviced_id=vehicle_id,
                total_cost=service_package.base_cost,
                created_at=datetime.now().date(),
                updated_at=datetime.now().date(),
            )
            db.session.add(appointment)
            db.session.commit()

            logging.info(f"Service appointment scheduled: {appointment.appt_id}")
            flash("Service appointment scheduled successfully!", "success")
            return redirect(url_for('routes.generate_service_bill', appointment_id=appointment.appt_id))

        except Exception as e:
            logging.error(f"Error scheduling service: {e}")
            flash("An error occurred while scheduling the service.", "danger")
            return redirect('/service')


        

import os
from flask import send_file

@bp.route('/service_bill/<int:appointment_id>', methods=['GET'])
def generate_service_bill(appointment_id):
    """Generate and display or download the service bill."""
    try:
        # Fetch appointment, customer, and vehicle details
        appointment = ServiceAppointment.query.get(appointment_id)
        if not appointment:
            logging.warning(f"Service appointment not found: {appointment_id}")
            flash("Service appointment not found.", "danger")
            return redirect('/service')

        customer = appointment.customer
        vehicle = appointment.vehicle
        if not customer or not vehicle:
            logging.warning(f"Missing customer or vehicle details for Appointment ID: {appointment_id}")
            flash("Associated customer or vehicle details are missing.", "danger")
            return redirect('/service')

        # Prepare data for the bill
        bill_data = {
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "customer_phone": customer.phone or "N/A",
            "customer_email": customer.email or "N/A",
            "vehicle_details": f"{vehicle.make} {vehicle.model} ({vehicle.year})",
            "appt_date": appointment.appt_date.strftime('%Y-%m-%d'),
            "arrival_time": appointment.arrival_time.strftime('%H:%M'),
            "completion_time": appointment.completion_time.strftime('%H:%M') if appointment.completion_time else "N/A",
            "total_cost": f"${appointment.total_cost:.2f}" if appointment.total_cost else "N/A",
        }

        # Ensure the directory exists
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Generate the PDF
        pdf_file = os.path.join(temp_dir, f"service_bill_{appointment_id}.pdf")
        c = canvas.Canvas(pdf_file)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 800, "Car Dealership Service Bill")
        c.setFont("Helvetica", 12)
        c.drawString(100, 770, f"Customer Name: {bill_data['customer_name']}")
        c.drawString(100, 750, f"Phone: {bill_data['customer_phone']}")
        c.drawString(100, 730, f"Email: {bill_data['customer_email']}")
        c.drawString(100, 710, f"Vehicle: {bill_data['vehicle_details']}")
        c.drawString(100, 690, f"Appointment Date: {bill_data['appt_date']}")
        c.drawString(100, 670, f"Arrival Time: {bill_data['arrival_time']}")
        c.drawString(100, 650, f"Completion Time: {bill_data['completion_time']}")
        c.drawString(100, 630, f"Total Cost: {bill_data['total_cost']}")
        c.drawString(100, 600, "Thank you for your business!")
        c.save()

        # Serve the PDF
        return send_file(
            pdf_file,
            as_attachment=True,
            download_name=f"service_bill_{appointment_id}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        logging.error(f"Error generating service bill: {e}")
        flash("An error occurred while generating the service bill.", "danger")
        return redirect('/service')
    finally:
        # Cleanup: Remove the generated PDF file after it is served
        if os.path.exists(pdf_file):
            os.remove(pdf_file)
