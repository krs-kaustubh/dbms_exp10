import sys
import pymysql

# Edit your MySQL connection settings here if different:
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "sams",
    "password": "krs312",
    "port": 3306,
    "charset": "utf8mb4"
}

if len(sys.argv) > 1:
    MYSQL_CONFIG["password"] = sys.argv[1]

print(f"Connecting to MySQL on {MYSQL_CONFIG['host']} as {MYSQL_CONFIG['user']}...")

try:
    conn = pymysql.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    print("✓ Connected to MySQL successfully!")

    # Read schema
    with open("schema_mysql.sql", "r") as f:
        sql_commands = f.read().split(";")

    for cmd in sql_commands:
        cmd = cmd.strip()
        if cmd:
            cur.execute(cmd)

    print("✓ Database 'societydb' and all 13 tables created!")

    # Populate sample data if empty
    cur.execute("USE societydb;")
    cur.execute("SELECT COUNT(*) FROM resident;")
    if cur.fetchone()[0] == 0:
        print("Populating initial Exp-4 sample records...")
        sample_inserts = [
            # Residents
            "INSERT INTO resident (resident_id, name, apartment_no, contact_no, email, status) VALUES "
            "(101, 'Aarav Raj Mehta', 'A-101', '9876543210', 'aarav.mehta@email.com', 'Approved'),"
            "(102, 'Sara Khan', 'B-204', '9988776655', 'sara.khan@email.com', 'Approved'),"
            "(103, 'Rohan Vijay Shah', 'C-305', '9876501234', 'rohan.shah@email.com', 'Approved'),"
            "(104, 'Anaya Patel', 'A-302', '9898989898', 'anaya.patel@email.com', 'Approved'),"
            "(105, 'Kabir Amit Joshi', 'B-110', '9000011111', 'kabir.joshi@email.com', 'Approved');",

            # Amenities
            "INSERT INTO amenity (amenity_id, name, location, operating_hours, capacity, amenity_type) VALUES "
            "(201, 'Gym', 'Block A Ground Floor', '06:00-22:00', 40, 'Gym'),"
            "(202, 'Community Hall', 'Clubhouse First Floor', '09:00-23:00', 150, 'Community_Hall'),"
            "(203, 'Swimming Pool', 'Clubhouse Ground Floor', '07:00-21:00', 60, 'Pool'),"
            "(204, 'Badminton Court', 'Sports Complex', '06:00-22:00', 20, 'Sports_Court'),"
            "(205, 'Yoga Studio', 'Clubhouse Second Floor', '06:00-21:00', 30, 'Gym');",

            # Subtypes
            "INSERT INTO pool (amenity_id, depth_ft) VALUES (203, 5.00);",
            "INSERT INTO sports_court (amenity_id, sport_type) VALUES (204, 'Badminton');",
            "INSERT INTO equipment (amenity_id, equipment_no, equipment_name, equipment_condition) VALUES "
            "(201, 1, 'Treadmill', 'Good'),"
            "(201, 2, 'Bench Press', 'Good'),"
            "(201, 3, 'Dumbbell Set', 'New');",

            # Staff
            "INSERT INTO staff (staff_id, name, contact_no, salary, shift_timing, staff_type, amenity_id) VALUES "
            "(301, 'Vikram Singh', '9811111111', 32000.00, '06:00-14:00', 'Trainer', 201),"
            "(302, 'Neha Verma', '9822222222', 45000.00, '09:00-18:00', 'Support_Staff', 202),"
            "(303, 'Imran Ali', '9833333333', 28000.00, '07:00-15:00', 'Support_Staff', 203),"
            "(304, 'Pooja Nair', '9844444444', 30000.00, '14:00-22:00', 'Support_Staff', 204),"
            "(305, 'Rahul Das', '9855555555', 29000.00, '06:00-14:00', 'Trainer', 205);",

            "INSERT INTO support_staff (staff_id, designation) VALUES "
            "(302, 'Facility Manager'),"
            "(303, 'Pool Attendant'),"
            "(304, 'Sports Assistant');",

            "INSERT INTO trainer (staff_id, specialization_area) VALUES "
            "(301, 'Strength Training'),"
            "(305, 'Yoga');",

            # Bookings
            "INSERT INTO booking (booking_id, booking_date, time_slot, status, resident_id, amenity_id) VALUES "
            "(501, '2026-09-10', '18:00-20:00', 'Confirmed', 101, 202),"
            "(502, '2026-09-11', '07:00-08:00', 'Confirmed', 102, 201),"
            "(503, '2026-09-12', '17:00-18:00', 'Pending', 103, 204),"
            "(504, '2026-09-13', '10:00-11:00', 'Confirmed', 104, 203),"
            "(505, '2026-09-14', '07:00-08:00', 'Cancelled', 105, 205);"
        ]
        for query in sample_inserts:
            cur.execute(query)
        conn.commit()
        print("✓ Sample data inserted successfully!")

    conn.commit()
    cur.close()
    conn.close()
    print("✓ Setup complete! You can now start the web application.")

except pymysql.MySQLError as err:
    print(f"MySQL Error: {err}")
    print("If password is required, run: python3 setup_db.py <your_mysql_password>")
