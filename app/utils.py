from datetime import datetime

def parse_date(date_string):
    """Parse a string into a Python datetime.date object."""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}. Expected format is YYYY-MM-DD.")

def calculate_total_profit(sale_price, purchase_price):
    """Calculate the profit for a vehicle sale."""
    return sale_price - purchase_price

def format_currency(value):
    """Format a number as currency."""
    return f"${value:,.2f}"
