from app import db

class Customer(db.Model):
    """Represents a customer in the database."""
    customer_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(40))
    address = db.Column(db.String(100))
    total_spent = db.Column(db.Numeric(10, 2))
    total_profit = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)

    vehicles = db.relationship('Vehicle', backref='owner', cascade='all, delete-orphan')
    appointments = db.relationship('ServiceAppointment', backref='customer', cascade='all, delete-orphan')


class Vehicle(db.Model):
    """Represents a vehicle in the database."""
    vehicle_id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(40))
    model = db.Column(db.String(40))
    year = db.Column(db.Integer)
    vin = db.Column(db.String(17), unique=True)
    purchase_price = db.Column(db.Numeric(10, 2))
    sale_price = db.Column(db.Numeric(10, 2))
    profit = db.Column(db.Numeric(10, 2))
    owner_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    sold_at = db.Column(db.Date)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)

    appointments = db.relationship('ServiceAppointment', backref='vehicle', cascade='all, delete-orphan')
    sales_stats = db.relationship('SalesStats', backref='vehicle', cascade='all, delete-orphan')


class ServiceAppointment(db.Model):
    """Represents a service appointment."""
    appt_id = db.Column(db.Integer, primary_key=True)
    appt_date = db.Column(db.Date)
    arrival_time = db.Column(db.Time)
    completion_time = db.Column(db.Time)
    service_customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    vehicle_serviced_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id'), nullable=False)
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)


class ServicePackage(db.Model):
    """Represents a service package."""
    pkg_id = db.Column(db.Integer, primary_key=True)
    pkg_name = db.Column(db.String(40))
    description = db.Column(db.String(100))
    base_cost = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.Date)
    updated_at = db.Column(db.Date)


class SalesStats(db.Model):
    """Represents sales statistics."""
    stats_id = db.Column(db.Integer, primary_key=True)
    vehicle_stat_id = db.Column(db.Integer, db.ForeignKey('vehicle.vehicle_id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cars_sold = db.Column(db.Integer)
    total_profit = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.Date)
