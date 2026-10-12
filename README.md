# SAMs Web Portal - DBMS Experiment 10 (MySQL)

Full-stack web application demonstrating **Front-End to RDBMS Database Connectivity** and execution of complete **CRUD (Create, Read, Update, Delete) operations** using Python Flask and MySQL.

---

## 📌 Features

- **Multi-Role Access Control:**
  - 👨‍💼 **Society Manager:** Universal access, approve/reject resident signups, review amenity booking requests, hire staff, create amenities.
  - 🏠 **Resident Portal:** Self-registration, book existing society amenities, propose new amenities, view personal visit history.
  - 🛠️ **Staff Console:** Amenity-linked view, live check-in / check-out of residents into entry logs.
- **Relational Integrity:** MySQL constraints (`PRIMARY KEY`, `FOREIGN KEY` with `ON DELETE CASCADE`, `UNIQUE`, `CHECK`).

---

## 🗂️ Project Structure

```text
.
├── app.py                  # Flask backend with PyMySQL queries
├── schema_mysql.sql        # MySQL 13-table relational schema
├── setup_db.py             # Database creation and seed script
├── run.sh                  # Application launcher
├── .gitignore              # Ignores venv and temp files
└── templates/              # Bootstrap 5 dark-mode templates
    ├── base.html           # Navbar & role switcher
    ├── manager.html        # Manager dashboard & approvals
    ├── resident.html       # Resident bookings & proposals
    ├── staff.html          # Staff check-in/out console
    ├── register.html       # Self-registration form
    └── edit_resident.html  # Update resident form
```

---

## 🚀 Setup & Execution

### 1. Configure MySQL User
```bash
sudo mysql -e "CREATE USER IF NOT EXISTS 'sams'@'localhost' IDENTIFIED BY 'krs312'; GRANT ALL PRIVILEGES ON *.* TO 'sams'@'localhost'; FLUSH PRIVILEGES;"
```

### 2. Initialize Database & Seed Data
```bash
python3 -m venv venv
./venv/bin/pip install flask pymysql mysql-connector-python
./venv/bin/python setup_db.py
```

### 3. Start the Server
```bash
bash run.sh
```
Open **`http://localhost:5000`** in your browser.

---

## 🔄 Experiment 10 CRUD Mappings

| CRUD Operation | Front-End UI Action | Flask Route | Executed SQL |
|---|---|---|---|
| **Create** | New Resident Signup Form | `POST /register` | `INSERT INTO resident (...) VALUES (...)` |
| **Read** | Manager Dashboard Resident Table | `GET /manager` | `SELECT * FROM resident ORDER BY resident_id` |
| **Update** | Edit Resident Details Form | `POST /residents/edit/<id>` | `UPDATE resident SET name=..., ... WHERE resident_id=...` |
| **Delete** | Delete Resident Button | `POST /residents/delete/<id>` | `DELETE FROM resident WHERE resident_id=...` |
