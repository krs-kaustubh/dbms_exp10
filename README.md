# SAMs: Society Amenities Management System

DBMS Experiment 10: a web front end connected to a MySQL database, performing CRUD operations (Create, Read, Update, Delete) on the **Resident** entity.

Built with Python (Flask + PyMySQL) and MySQL. The UI is plain HTML/CSS/JS served by the app itself, so it works **without internet access**.

## Run it on a new computer (after `git clone`)

**You need:** Python 3.9+ and a running MySQL server (8.0 recommended). If MySQL is missing, install MySQL Community Server or XAMPP first.

```bash
git clone https://github.com/krs-kaustubh/dbms_exp10.git
cd dbms_exp10
```

**1. Install the dependencies**

| Windows (PowerShell / cmd) | Linux / macOS |
|---|---|
| `python -m venv venv` | `python3 -m venv venv` |
| `venv\Scripts\activate` | `source venv/bin/activate` |
| `pip install -r requirements.txt` | `pip install -r requirements.txt` |

**2. Create the database** (one time)

```bash
python setup_db.py
```

It tries to log in to MySQL as `root` with no password. If that fails it asks for your MySQL host, user and password, remembers them in a local `.env` file (never committed), then creates the `sams_db` database, 13 tables and sample data.

**3. Start the app**

```bash
python app.py
```

Open **http://localhost:5000**.

### Troubleshooting

| Problem | Fix |
|---|---|
| `Can't connect to MySQL server` | MySQL is not running. Start the MySQL service (or XAMPP's MySQL). |
| `Access denied for user 'root'` (Ubuntu) | Ubuntu's root account only works through `sudo`. Create a normal user: `sudo mysql -e "CREATE USER 'sams'@'localhost' IDENTIFIED BY 'yourpassword'; GRANT ALL ON sams_db.* TO 'sams'@'localhost';"` then run `python setup_db.py` and enter that user. |
| `python` not found on Windows | Try `py` instead of `python`. |
| Want a clean database again | `python setup_db.py --reset` (drops and recreates `sams_db`). |
| Different DB name or port | Edit `.env` (see `.env.example`). |

The database is called `sams_db`, so it never touches the `societydb` database from the earlier experiments.

## What the app does

Three portals, switched from the sidebar (this is a lab demo, so there is no login):

| Portal | What you can do |
|---|---|
| **Manager** | Approve/reject resident sign-ups and booking requests, add/edit/delete residents, create amenities, hire staff, approve amenity suggestions, view the entry log. |
| **Resident** | Book an amenity, suggest a new amenity, see own bookings and visits. Booking is only allowed after the manager approves the resident. |
| **Staff** | Linked to one amenity: check residents in and out, see that amenity's bookings. |

### Suggested demo order

1. **Resident sign-up** (sidebar) creates a resident with status *Pending*.
2. **Manager → Residents** shows it; approve it, edit it, or delete it.
3. **Resident** portal: switch to the approved resident and request a booking.
4. **Manager → Bookings**: accept the request.
5. **Staff** portal: check the resident in, then log the exit. The **Entry log** tab shows it.

## CRUD mapping (the Experiment 10 requirement)

| Operation | UI action | Route | SQL |
|---|---|---|---|
| **Create** | Resident sign-up form | `POST /register` | `INSERT INTO resident (...) VALUES (...)` |
| **Read** | Manager → Residents tab | `GET /manager` | `SELECT * FROM resident` |
| **Update** | Edit button, then Save | `POST /residents/edit/<id>` | `UPDATE resident SET ... WHERE resident_id = <id>` |
| **Delete** | Delete button (asks to confirm) | `POST /residents/delete/<id>` | `DELETE FROM resident WHERE resident_id = <id>` |

All queries use parameter placeholders (`%s`), so user input is never pasted into SQL text. Deleting a resident also removes their bookings, enrollments, entry logs and amenity suggestions through `ON DELETE CASCADE`.

## Project layout

```text
app.py              Flask routes and SQL queries
config.py           Reads DB settings from environment / .env
setup_db.py         Creates the database, tables and sample data
schema_mysql.sql    13-table schema (keys, CHECK, UNIQUE, cascades)
seed_mysql.sql      Sample data (same residents/amenities as Experiment 4)
requirements.txt    Flask, PyMySQL, cryptography
static/             style.css and app.js (no external libraries)
templates/          base, manager, resident, staff, register, edit_resident
```
