from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from DataB import get_db_conn

app = Flask(__name__)
app.secret_key = "staffsync_secret_key"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_conn()

        admin = conn.execute(
            "SELECT * FROM admins WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if admin and check_password_hash(
            admin["password"],
            password
        ):

            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["first_name"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


@app.route("/admin_panel.html")
def dashboard():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_conn()

    employees = conn.execute(
        "SELECT * FROM employees ORDER BY id DESC"
    ).fetchall()

    total_employees = conn.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    total_departments = conn.execute(
        "SELECT COUNT(DISTINCT department) FROM employees"
    ).fetchone()[0]

    average_salary = conn.execute(
        "SELECT AVG(salary) FROM employees"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin_panel.html",
        employees=employees,
        total_employees=total_employees,
        total_departments=total_departments,
        average_salary=round(average_salary or 0, 2)
    )


@app.route("/add_employee", methods=["POST"])
def add_employee():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    department = request.form["department"]
    salary = request.form["salary"]

    conn = get_db_conn()

    conn.execute(
        """
        INSERT INTO employees
        (
            first_name,
            last_name,
            email,
            department,
            salary
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            first_name,
            last_name,
            email,
            department,
            salary
        )
    )

    conn.commit()
    conn.close()

    flash("Employee added successfully")

    return redirect(url_for("dashboard"))


@app.route("/edit_employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_conn()

    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        department = request.form["department"]
        salary = request.form["salary"]

        conn.execute(
            """
            UPDATE employees
            SET
                first_name = ?,
                last_name = ?,
                email = ?,
                department = ?,
                salary = ?
            WHERE id = ?
            """,
            (
                first_name,
                last_name,
                email,
                department,
                salary,
                id
            )
        )

        conn.commit()
        conn.close()

        flash("Employee updated successfully")

        return redirect(url_for("dashboard"))

    conn.close()

    return render_template(
        "edit_employee.html",
        employee=employee
    )


@app.route("/delete_employee/<int:id>")
def delete_employee(id):

    if "admin_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_conn()

    conn.execute(
        "DELETE FROM employees WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Employee deleted")

    return redirect(url_for("dashboard"))


@app.route("/search")
def search():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    query = request.args.get("query", "")

    conn = get_db_conn()

    employees = conn.execute(
        """
        SELECT *
        FROM employees
        WHERE
            first_name LIKE ?
            OR last_name LIKE ?
            OR department LIKE ?
            OR email LIKE ?
        """,
        (
            f"%{query}%",
            f"%{query}%",
            f"%{query}%",
            f"%{query}%"
        )
    ).fetchall()

    total_employees = len(employees)

    total_departments = conn.execute(
        "SELECT COUNT(DISTINCT department) FROM employees"
    ).fetchone()[0]

    average_salary = conn.execute(
        "SELECT AVG(salary) FROM employees"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin_panel.html",
        employees=employees,
        total_employees=total_employees,
        total_departments=total_departments,
        average_salary=round(average_salary or 0, 2)
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )