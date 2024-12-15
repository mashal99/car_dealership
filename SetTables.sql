-- Drop all tables if they exist
DROP TABLE IF EXISTS service_appointment;
DROP TABLE IF EXISTS service_package;
DROP TABLE IF EXISTS sales_stats;
DROP TABLE IF EXISTS vehicle;
DROP TABLE IF EXISTS customer;

-- Create the Customer table
CREATE TABLE customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(40) NOT NULL,
    last_name VARCHAR(40) NOT NULL,
    phone VARCHAR(15) DEFAULT NULL,
    email VARCHAR(40) DEFAULT NULL,
    address VARCHAR(100) DEFAULT NULL,
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    total_profit DECIMAL(10,2) DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the Vehicle table
CREATE TABLE vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    make VARCHAR(40),
    model VARCHAR(40),
    year INT,
    vin VARCHAR(17) UNIQUE,
    purchase_price DECIMAL(10,2) DEFAULT 0.00,
    sale_price DECIMAL(10,2) DEFAULT NULL,
    profit DECIMAL(10,2) DEFAULT NULL,
    owner_id INT NOT NULL,
    sold_at DATE DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES customer(customer_id) ON DELETE CASCADE
);

-- Create the Service Appointment table
CREATE TABLE service_appointment (
    appt_id INT AUTO_INCREMENT PRIMARY KEY,
    appt_date DATE NOT NULL,
    arrival_time TIME NOT NULL,
    completion_time TIME DEFAULT NULL,
    service_customer_id INT NOT NULL,
    vehicle_serviced_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (service_customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_serviced_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE
);

-- Create the Service Package table
CREATE TABLE service_package (
    pkg_id INT AUTO_INCREMENT PRIMARY KEY,
    pkg_name VARCHAR(40) NOT NULL,
    description VARCHAR(100) DEFAULT NULL,
    base_cost DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the Sales Statistics table
CREATE TABLE sales_stats (
    stats_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_stat_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    cars_sold INT DEFAULT 0,
    total_profit DECIMAL(10,2) DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_stat_id) REFERENCES vehicle(vehicle_id) ON DELETE CASCADE
);
