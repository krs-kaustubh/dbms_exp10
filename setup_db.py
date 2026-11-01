"""One-time database setup for SAMs. Works on Windows, Linux and macOS.

    python setup_db.py            create database + tables + sample data
    python setup_db.py --reset    drop the SAMs database first, then recreate

If the default MySQL login (see config.py / .env) does not work, the script
asks for your MySQL host, user and password and saves them to `.env`.
"""
import getpass
import sys

import pymysql

import config

ROOT = config.BASE_DIR


def run_script(cur, path):
    """Execute a .sql file statement by statement (comments are stripped)."""
    lines = []
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    for statement in "\n".join(lines).split(";"):
        if statement.strip():
            cur.execute(statement)


def connect(host, port, user, password):
    return pymysql.connect(host=host, port=port, user=user, password=password,
                           charset="utf8mb4", autocommit=True)


def get_connection():
    host, port = config.DB_HOST, config.DB_PORT
    user, password = config.DB_USER, config.DB_PASSWORD
    try:
        return connect(host, port, user, password), False
    except pymysql.MySQLError as err:
        print(f"Could not log in to MySQL as '{user}'@'{host}': {err}")

    print("\nEnter your MySQL login (college PCs usually use user 'root'):")
    for _ in range(3):
        host = input(f"  Host [{config.DB_HOST}]: ").strip() or config.DB_HOST
        user = input(f"  User [{config.DB_USER}]: ").strip() or config.DB_USER
        password = getpass.getpass("  Password (blank if none): ")
        try:
            return connect(host, port, user, password), (host, port, user, password)
        except pymysql.MySQLError as err:
            print(f"  Login failed: {err}\n")
    sys.exit("Giving up. Check that MySQL is running and the login is correct.")


def save_env(host, port, user, password):
    config.ENV_FILE.write_text(
        f"DB_HOST={host}\nDB_PORT={port}\nDB_USER={user}\nDB_PASSWORD={password}\n"
        f"DB_NAME={config.DB_NAME}\n", encoding="utf-8")
    print(f"Saved login to {config.ENV_FILE.name} (not committed to git).")


def main():
    reset = "--reset" in sys.argv
    conn, new_login = get_connection()
    cur = conn.cursor()
    db = config.DB_NAME

    cur.execute("SHOW DATABASES LIKE %s", (db,))
    exists = cur.fetchone() is not None
    if exists and not reset:
        cur.execute(f"USE `{db}`")
        cur.execute("SHOW TABLES LIKE 'resident'")
        if cur.fetchone():
            print(f"Database '{db}' is already set up. Use --reset to rebuild it.")
            if new_login:
                save_env(*new_login)
            return
    if exists:
        cur.execute(f"DROP DATABASE `{db}`")
        print(f"Dropped database '{db}'.")

    cur.execute(f"CREATE DATABASE `{db}` CHARACTER SET utf8mb4")
    cur.execute(f"USE `{db}`")
    run_script(cur, "schema_mysql.sql")
    print("Created 13 tables.")
    run_script(cur, "seed_mysql.sql")
    print("Inserted sample data.")
    if new_login:
        save_env(*new_login)
    conn.close()
    print("\nDone. Start the app with:  python app.py")


if __name__ == "__main__":
    main()
