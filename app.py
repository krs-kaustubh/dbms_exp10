import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)
app.secret_key = "sams_mysql_secret_key"

# =========================================================
# MySQL DATABASE CONFIGURATION
# =========================================================
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "sams",
    "password": "krs312",
    "database": "societydb",
    "port": 3306,
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
    "autocommit": True
}

def get_db():
    return pymysql.connect(**MYSQL_CONFIG)

def get_next_id(table, col, default=101):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COALESCE(MAX({col}), {default - 1}) + 1 AS next_id FROM {table};")
    res = cur.fetchone()
    next_id = res["next_id"]
    cur.close()
    conn.close()
    return next_id

@app.before_request
def setup_role():
    if "role" not in session:
        session["role"] = "manager"

@app.route("/switch-role", methods=["POST"])
def switch_role():
    role = request.form.get("role", "manager")
    session["role"] = role

    if role == "resident":
        session["resident_id"] = int(request.form.get("resident_id", 101))
        return redirect(url_for("resident_portal"))
    elif role == "staff":
        session["staff_id"] = int(request.form.get("staff_id", 301))
        return redirect(url_for("staff_portal"))
    else:
        return redirect(url_for("manager_portal"))

# =========================================================
# 1. SOCIETY MANAGER PORTAL (Universal Access)
# =========================================================
@app.route("/")
@app.route("/manager")
def manager_portal():
    session["role"] = "manager"
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) AS count FROM resident;")
        total_res = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) AS count FROM resident WHERE status = 'Pending';")
        pending_res_count = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) AS count FROM booking WHERE status = 'Pending';")
        pending_bk_count = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) AS count FROM amenity_proposal WHERE status = 'Pending';")
        pending_prop_count = cur.fetchone()["count"]

        cur.execute("SELECT * FROM resident WHERE status = 'Pending' ORDER BY resident_id;")
        pending_residents = cur.fetchall()

        cur.execute("SELECT * FROM resident ORDER BY resident_id;")
        all_residents = cur.fetchall()

        cur.execute("SELECT * FROM amenity ORDER BY amenity_id;")
        amenities = cur.fetchall()

        cur.execute("""
            SELECT s.*, a.name AS amenity_name
            FROM staff s
            LEFT JOIN amenity a ON s.amenity_id = a.amenity_id
            ORDER BY s.staff_id;
        """)
        staff_members = cur.fetchall()

        cur.execute("""
            SELECT b.*, r.name AS resident_name, a.name AS amenity_name
            FROM booking b
            JOIN resident r ON b.resident_id = r.resident_id
            JOIN amenity a ON b.amenity_id = a.amenity_id
            ORDER BY b.booking_id DESC;
        """)
        bookings = cur.fetchall()

        cur.execute("""
            SELECT ap.*, r.name AS resident_name, r.apartment_no
            FROM amenity_proposal ap
            JOIN resident r ON ap.resident_id = r.resident_id
            ORDER BY ap.proposal_id DESC;
        """)
        proposals = cur.fetchall()

        cur.execute("""
            SELECT el.*, r.name AS resident_name, a.name AS amenity_name, s.name AS staff_name
            FROM entry_log el
            JOIN resident r ON el.resident_id = r.resident_id
            JOIN amenity a ON el.amenity_id = a.amenity_id
            LEFT JOIN staff s ON el.recorded_by = s.staff_id
            ORDER BY el.entry_time DESC LIMIT 20;
        """)
        entry_logs = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "manager.html",
            total_res=total_res,
            pending_res_count=pending_res_count,
            pending_bk_count=pending_bk_count,
            pending_prop_count=pending_prop_count,
            pending_residents=pending_residents,
            all_residents=all_residents,
            amenities=amenities,
            staff_members=staff_members,
            bookings=bookings,
            proposals=proposals,
            entry_logs=entry_logs
        )
    except Exception as e:
        flash(f"MySQL connection error: {e}. Ensure MySQL is running on port 3306 and societydb is setup.", "danger")
        return render_template("manager.html")

@app.route("/manager/staff/add", methods=["POST"])
def add_staff():
    try:
        staff_id = get_next_id("staff", "staff_id", 306)
        name = request.form["name"]
        contact = request.form["contact_no"]
        salary = request.form["salary"]
        shift = request.form["shift_timing"]
        staff_type = request.form["staff_type"]
        amenity_id = request.form["amenity_id"]
        sub_info = request.form.get("sub_info", "General")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO staff (staff_id, name, contact_no, salary, shift_timing, staff_type, amenity_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (staff_id, name, contact, salary, shift, staff_type, amenity_id))

        if staff_type == "Trainer":
            cur.execute("INSERT INTO trainer (staff_id, specialization_area) VALUES (%s, %s);", (staff_id, sub_info))
        else:
            cur.execute("INSERT INTO support_staff (staff_id, designation) VALUES (%s, %s);", (staff_id, sub_info))

        cur.close()
        conn.close()
        flash(f"Staff member {name} (ID: {staff_id}) hired successfully in MySQL!", "success")
    except Exception as e:
        flash(f"Error hiring staff: {e}", "danger")
    return redirect(url_for("manager_portal"))

@app.route("/manager/amenity/add", methods=["POST"])
def add_amenity():
    try:
        amenity_id = get_next_id("amenity", "amenity_id", 206)
        name = request.form["name"]
        location = request.form["location"]
        operating_hours = request.form["operating_hours"]
        capacity = request.form["capacity"]
        amenity_type = request.form["amenity_type"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO amenity (amenity_id, name, location, operating_hours, capacity, amenity_type)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (amenity_id, name, location, operating_hours, capacity, amenity_type))

        if amenity_type == "Pool":
            cur.execute("INSERT INTO pool (amenity_id, depth_ft) VALUES (%s, 5.0);", (amenity_id,))
        elif amenity_type == "Sports_Court":
            cur.execute("INSERT INTO sports_court (amenity_id, sport_type) VALUES (%s, %s);", (amenity_id, name))

        cur.close()
        conn.close()
        flash(f"New Amenity '{name}' (ID: {amenity_id}) established in MySQL!", "success")
    except Exception as e:
        flash(f"Error creating amenity: {e}", "danger")
    return redirect(url_for("manager_portal"))

@app.route("/manager/resident/<int:res_id>/<action>", methods=["POST"])
def review_resident(res_id, action):
    new_status = "Approved" if action == "approve" else "Rejected"
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE resident SET status = %s WHERE resident_id = %s;", (new_status, res_id))
        cur.close()
        conn.close()
        flash(f"Resident {res_id} marked as {new_status}!", "success")
    except Exception as e:
        flash(f"Action failed: {e}", "danger")
    return redirect(url_for("manager_portal"))

@app.route("/manager/booking/<int:bk_id>/<action>", methods=["POST"])
def review_booking(bk_id, action):
    new_status = "Confirmed" if action == "approve" else "Cancelled"
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE booking SET status = %s WHERE booking_id = %s;", (new_status, bk_id))
        cur.close()
        conn.close()
        flash(f"Booking {bk_id} marked as {new_status}!", "success")
    except Exception as e:
        flash(f"Action failed: {e}", "danger")
    return redirect(url_for("manager_portal"))

@app.route("/manager/proposal/<int:p_id>/<action>", methods=["POST"])
def review_proposal(p_id, action):
    try:
        conn = get_db()
        cur = conn.cursor()
        if action == "approve":
            cur.execute("SELECT * FROM amenity_proposal WHERE proposal_id = %s;", (p_id,))
            prop = cur.fetchone()
            if prop:
                new_amenity_id = get_next_id("amenity", "amenity_id", 206)
                cur.execute("""
                    INSERT INTO amenity (amenity_id, name, location, operating_hours, capacity, amenity_type)
                    VALUES (%s, %s, 'Clubhouse Complex', '06:00-22:00', 30, %s);
                """, (new_amenity_id, prop["amenity_name"], prop["suggested_type"]))
                cur.execute("UPDATE amenity_proposal SET status = 'Approved' WHERE proposal_id = %s;", (p_id,))
                flash(f"Proposal approved! Amenity '{prop['amenity_name']}' created automatically.", "success")
        else:
            cur.execute("UPDATE amenity_proposal SET status = 'Rejected' WHERE proposal_id = %s;", (p_id,))
            flash("Amenity proposal rejected.", "info")
        cur.close()
        conn.close()
    except Exception as e:
        flash(f"Error reviewing proposal: {e}", "danger")
    return redirect(url_for("manager_portal"))

# =========================================================
# 2. RESIDENT PORTAL (CRUD on Resident Entity)
# =========================================================
@app.route("/resident")
def resident_portal():
    session["role"] = "resident"
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT resident_id FROM resident ORDER BY resident_id LIMIT 1;")
        first_r = cur.fetchone()
        default_id = first_r["resident_id"] if first_r else None

        res_id = session.get("resident_id") or default_id
        session["resident_id"] = res_id

        cur.execute("SELECT * FROM resident WHERE resident_id = %s;", (res_id,))
        resident = cur.fetchone()

        cur.execute("""
            SELECT b.*, a.name AS amenity_name, a.location
            FROM booking b
            JOIN amenity a ON b.amenity_id = a.amenity_id
            WHERE b.resident_id = %s
            ORDER BY b.booking_id DESC;
        """, (res_id,))
        my_bookings = cur.fetchall()

        cur.execute("""
            SELECT * FROM amenity_proposal WHERE resident_id = %s ORDER BY proposal_id DESC;
        """, (res_id,))
        my_proposals = cur.fetchall()

        cur.execute("""
            SELECT el.*, a.name AS amenity_name
            FROM entry_log el
            JOIN amenity a ON el.amenity_id = a.amenity_id
            WHERE el.resident_id = %s
            ORDER BY el.entry_time DESC;
        """, (res_id,))
        my_entries = cur.fetchall()

        cur.execute("SELECT * FROM amenity ORDER BY name;")
        amenities = cur.fetchall()

        cur.execute("SELECT resident_id, name, status FROM resident ORDER BY resident_id;")
        all_residents = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "resident.html",
            resident=resident,
            my_bookings=my_bookings,
            my_proposals=my_proposals,
            my_entries=my_entries,
            amenities=amenities,
            all_residents=all_residents
        )
    except Exception as e:
        flash(f"Resident portal error: {e}", "danger")
        return render_template("resident.html")

# Create: Resident Self-Registration (INSERT)
@app.route("/register", methods=["GET", "POST"])
def register_resident():
    if request.method == "POST":
        try:
            res_id = get_next_id("resident", "resident_id", 106)
            name = request.form["name"]
            apt_no = request.form["apartment_no"]
            contact = request.form["contact_no"]
            email = request.form["email"]

            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO resident (resident_id, name, apartment_no, contact_no, email, status)
                VALUES (%s, %s, %s, %s, %s, 'Pending');
            """, (res_id, name, apt_no, contact, email))
            cur.close()
            conn.close()

            flash(f"Registration submitted (Assigned ID: {res_id})! Awaiting Manager approval.", "info")
            session["resident_id"] = res_id
            return redirect(url_for("resident_portal"))
        except Exception as e:
            flash(f"Registration failed: {e}", "danger")

    return render_template("register.html")

# Update: Edit Resident Details (UPDATE)
@app.route("/residents/edit/<int:res_id>", methods=["GET", "POST"])
def edit_resident(res_id):
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        try:
            name = request.form["name"]
            apt_no = request.form["apartment_no"]
            contact = request.form["contact_no"]
            email = request.form["email"]

            cur.execute("""
                UPDATE resident
                SET name = %s, apartment_no = %s, contact_no = %s, email = %s
                WHERE resident_id = %s;
            """, (name, apt_no, contact, email, res_id))
            flash(f"Resident {res_id} details updated successfully in MySQL!", "success")
            cur.close()
            conn.close()
            return redirect(url_for("manager_portal"))
        except Exception as e:
            flash(f"Error updating resident: {e}", "danger")

    cur.execute("SELECT * FROM resident WHERE resident_id = %s;", (res_id,))
    resident = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit_resident.html", resident=resident)

# Delete: Remove Resident (DELETE)
@app.route("/residents/delete/<int:res_id>", methods=["POST"])
def delete_resident(res_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM resident WHERE resident_id = %s;", (res_id,))
        cur.close()
        conn.close()
        flash(f"Resident {res_id} deleted successfully from MySQL!", "info")
    except Exception as e:
        flash(f"Error deleting resident: {e}", "danger")
    return redirect(url_for("manager_portal"))

# Resident: Request Booking
@app.route("/resident/request-booking", methods=["POST"])
def request_booking():
    res_id = request.form.get("resident_id") or session.get("resident_id")
    try:
        conn = get_db()
        cur = conn.cursor()

        if not res_id:
            cur.execute("SELECT resident_id FROM resident ORDER BY resident_id LIMIT 1;")
            first_r = cur.fetchone()
            res_id = first_r["resident_id"] if first_r else None
            session["resident_id"] = res_id

        amenity_id = request.form["amenity_id"]
        b_date = request.form["booking_date"]
        time_slot = request.form["time_slot"]
        b_id = get_next_id("booking", "booking_id", 507)

        cur.execute("SELECT status FROM resident WHERE resident_id = %s;", (res_id,))
        r = cur.fetchone()
        if not r or r["status"] != "Approved":
            flash("You cannot book amenities until your residency is Approved by the Manager!", "warning")
            cur.close()
            conn.close()
            return redirect(url_for("resident_portal"))

        cur.execute("""
            INSERT INTO booking (booking_id, resident_id, amenity_id, booking_date, time_slot, status)
            VALUES (%s, %s, %s, %s, %s, 'Pending');
        """, (b_id, res_id, amenity_id, b_date, time_slot))
        cur.close()
        conn.close()

        flash("Booking request sent! Waiting for Manager confirmation.", "success")
    except Exception as e:
        flash(f"Booking error: {e}", "danger")

    return redirect(url_for("resident_portal"))

# Resident: Propose New Amenity
@app.route("/resident/propose-amenity", methods=["POST"])
def propose_amenity():
    res_id = request.form.get("resident_id") or session.get("resident_id")
    name = request.form["amenity_name"]
    suggested_type = request.form["suggested_type"]
    reason = request.form.get("reason", "")

    try:
        conn = get_db()
        cur = conn.cursor()

        if not res_id:
            cur.execute("SELECT resident_id FROM resident ORDER BY resident_id LIMIT 1;")
            first_r = cur.fetchone()
            res_id = first_r["resident_id"] if first_r else None
            session["resident_id"] = res_id

        if not res_id:
            flash("No resident account found. Please register first!", "warning")
            cur.close()
            conn.close()
            return redirect(url_for("register_resident"))

        cur.execute("""
            INSERT INTO amenity_proposal (resident_id, amenity_name, suggested_type, reason, status)
            VALUES (%s, %s, %s, %s, 'Pending');
        """, (res_id, name, suggested_type, reason))
        cur.close()
        conn.close()
        flash("Amenity proposal submitted to Society Manager!", "success")
    except Exception as e:
        flash(f"Error submitting proposal: {e}", "danger")

    return redirect(url_for("resident_portal"))

# =========================================================
# 3. STAFF PORTAL
# =========================================================
@app.route("/staff")
def staff_portal():
    session["role"] = "staff"
    staff_id = session.get("staff_id", 301)

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT s.*, a.name AS amenity_name, a.location, a.operating_hours
            FROM staff s
            JOIN amenity a ON s.amenity_id = a.amenity_id
            WHERE s.staff_id = %s;
        """, (staff_id,))
        staff = cur.fetchone()

        if not staff:
            cur.close()
            conn.close()
            flash("Staff member not found.", "warning")
            return redirect(url_for("manager_portal"))

        amenity_id = staff["amenity_id"]

        cur.execute("""
            SELECT b.*, r.name AS resident_name, r.apartment_no, r.contact_no
            FROM booking b
            JOIN resident r ON b.resident_id = r.resident_id
            WHERE b.amenity_id = %s
            ORDER BY b.booking_date, b.time_slot;
        """, (amenity_id,))
        assigned_bookings = cur.fetchall()

        cur.execute("""
            SELECT el.*, r.name AS resident_name, r.apartment_no
            FROM entry_log el
            JOIN resident r ON el.resident_id = r.resident_id
            WHERE el.amenity_id = %s AND el.exit_time IS NULL
            ORDER BY el.entry_time DESC;
        """, (amenity_id,))
        active_entries = cur.fetchall()

        cur.execute("SELECT resident_id, name, apartment_no FROM resident WHERE status = 'Approved' ORDER BY name;")
        approved_residents = cur.fetchall()

        cur.execute("""
            SELECT s.staff_id, s.name, s.staff_type, a.name AS amenity_name
            FROM staff s JOIN amenity a ON s.amenity_id = a.amenity_id
            ORDER BY s.staff_id;
        """)
        all_staff = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "staff.html",
            staff=staff,
            assigned_bookings=assigned_bookings,
            active_entries=active_entries,
            approved_residents=approved_residents,
            all_staff=all_staff
        )
    except Exception as e:
        flash(f"Staff portal error: {e}", "danger")
        return render_template("staff.html")

@app.route("/staff/checkin", methods=["POST"])
def staff_checkin():
    staff_id = session.get("staff_id", 301)
    resident_id = request.form["resident_id"]
    amenity_id = request.form["amenity_id"]

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO entry_log (resident_id, amenity_id, entry_time, exit_time, recorded_by)
            VALUES (%s, %s, %s, NULL, %s);
        """, (resident_id, amenity_id, datetime.now(), staff_id))
        cur.close()
        conn.close()
        flash(f"Resident {resident_id} checked in!", "success")
    except Exception as e:
        flash(f"Check-in error: {e}", "danger")

    return redirect(url_for("staff_portal"))

@app.route("/staff/checkout", methods=["POST"])
def staff_checkout():
    resident_id = request.form["resident_id"]
    entry_time = request.form["entry_time"]

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE entry_log
            SET exit_time = %s
            WHERE resident_id = %s AND entry_time = %s;
        """, (datetime.now(), resident_id, entry_time))
        cur.close()
        conn.close()
        flash("Resident exit logged!", "info")
    except Exception as e:
        flash(f"Checkout error: {e}", "danger")

    return redirect(url_for("staff_portal"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
