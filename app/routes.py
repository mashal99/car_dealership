from flask import Blueprint, request, jsonify
from app.models import db, Customer, Car

bp = Blueprint('routes', __name__)

@bp.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    customer = Customer(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data['phone']
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({"message": "Customer added successfully!"})

@bp.route('/add_car', methods=['POST'])
def add_car():
    data = request.json
    car = Car(
        make=data['make'],
        model=data['model'],
        year=data['year'],
        vin=data['vin'],
        dealer_cost=data['dealer_cost'],
        purchase_price=data['purchase_price']
    )
    db.session.add(car)
    db.session.commit()
    return jsonify({"message": "Car added successfully!"})
