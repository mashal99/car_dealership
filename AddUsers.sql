-- Insert data into Customer table
INSERT INTO customer (first_name, last_name, phone, email, address, total_spent, total_profit)
VALUES 
    ('Liam', 'Miller', '123-234-3456', 'liammiller123@gmail.com', '100 Main St', 1000.20, 505.15),
    ('Fiona', 'Smith', '101-202-3003', 'fionasmith3@gmail.com', '220 5th Ave', 1256.32, 127.54),
    ('Ivor', 'Watson', '100-200-3000', 'ivorwatson400@hotmail.com', '521 Broad St', 5000.54, 883.29),
    ('Gary', 'Monroe', '010-020-0330', 'garymonroe1995@yahoo.com', '97 Summit St', 8884.23, 120.65);

-- Insert data into Vehicle table
INSERT INTO vehicle (make, model, year, vin, purchase_price, sale_price, profit, owner_id, sold_at)
VALUES 
    ('Toyota', 'Camry', 2015, '34164V643948209', 20243.21, 28554.23, 8311.02, 1, '2023-10-04'),
    ('Kia', 'Rio', 2012, '12745V143578642', 18554.64, 19948.49, 1393.85, 2, '2020-12-12'),
    ('Honda', 'Civic', 2008, '21542V678904323', 15221.30, 27382.39, 12161.09, 3, '2022-05-05');

-- Insert data into Service Appointment table
INSERT INTO service_appointment (appt_date, arrival_time, completion_time, service_customer_id, vehicle_serviced_id)
VALUES 
    ('2024-11-30', '09:30:00', '10:30:00', 1, 1),
    ('2024-12-07', '13:15:00', '14:30:00', 2, 2);

-- Insert data into Service Package table
INSERT INTO service_package (pkg_name, description, base_cost)
VALUES 
    ('Package 1', NULL, 150.00),
    ('Package 2', NULL, 250.00),
    ('Package 3', NULL, 350.00);

-- Insert data into Sales Statistics table
INSERT INTO sales_stats (vehicle_stat_id, start_date, end_date, cars_sold, total_profit)
VALUES 
    (1, '2020-12-15', '2023-10-05', 10, 12234.54),
    (2, '2020-10-01', '2023-11-11', 15, 14257.32);
