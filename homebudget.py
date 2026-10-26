from flask import Flask, render_template, request, redirect, url_for, send_file
import mysql.connector
import os

print("Project folder:", os.path.dirname(os.path.abspath(__file__)))
print("Templates folder exists:", os.path.isdir("templates"))
print("HTML file exists:", os.path.isfile("templates/index.html"))
import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import date
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


app = Flask(__name__)


# Connect to MySQL database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("DB_PASSWORD"),
        database="home_budget_db"
    )


# Get all categories
def get_categories():
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT category_id, category_name
            FROM categories
            ORDER BY category_name
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        con.close()


# Home page and transaction handling
@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    # Add a new income or expense
    if request.method == "POST":
        transaction_type = request.form.get("transaction_type", "")
        category_text = request.form.get("category_id", "")
        amount_text = request.form.get("amount", "").strip()
        transaction_date = request.form.get("transaction_date", "")
        description = request.form.get("description", "").strip()

        category_id = None
        amount = None

        try:
            category_id = int(category_text)
        except (ValueError, TypeError):
            error = "Please select a valid category."

        try:
            amount = Decimal(amount_text)

            if not amount.is_finite() or amount <= 0:
                raise ValueError

            if amount.as_tuple().exponent < -2:
                raise ValueError

        except (InvalidOperation, ValueError):
            error = "Enter a positive amount with up to 2 decimal places."

        if transaction_type not in ("Income", "Expense"):
            error = "Please select Income or Expense."

        try:
            parsed_date = date.fromisoformat(transaction_date)

            if parsed_date > date.today():
                error = "Date cannot be in the future."

        except (ValueError, TypeError):
            error = "Please select a valid date."

        if not error:
            con = None
            cursor = None

            try:
                con = get_connection()
                cursor = con.cursor()

                cursor.execute(
                    "SELECT category_id FROM categories WHERE category_id = %s",
                    (category_id,)
                )

                if cursor.fetchone() is None:
                    error = "Please select a valid category."

                else:
                    cursor.execute("""
                        INSERT INTO transactions
                        (
                            transaction_date,
                            transaction_type,
                            category_id,
                            amount,
                            description
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        transaction_date,
                        transaction_type,
                        category_id,
                        amount,
                        description or None
                    ))

                    con.commit()

            except mysql.connector.Error:
                if con:
                    con.rollback()

                error = (
                    "Unable to save transaction. "
                    "Check the database connection."
                )

            finally:
                if cursor:
                    cursor.close()

                if con and con.is_connected():
                    con.close()

            if not error:
                return redirect(url_for("home", added="1"))

    # Retrieve transaction history
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                t.transaction_id,
                t.transaction_date,
                t.transaction_type,
                c.category_name,
                t.amount,
                t.description
            FROM transactions t
            JOIN categories c
                ON t.category_id = c.category_id
            ORDER BY
                t.transaction_date DESC,
                t.transaction_id DESC
        """)

        transactions = cursor.fetchall()

    finally:
        cursor.close()
        con.close()

    # Calculate income, expenses and category totals using Pandas
    df = pd.DataFrame(transactions)

    income = 0.0
    expenses = 0.0
    category_totals = []

    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"])

        income = float(
            df.loc[
                df["transaction_type"] == "Income",
                "amount"
            ].sum()
        )

        expenses = float(
            df.loc[
                df["transaction_type"] == "Expense",
                "amount"
            ].sum()
        )

        expense_df = df[
            df["transaction_type"] == "Expense"
        ]

        if not expense_df.empty:
            category_totals = (
                expense_df.groupby("category_name")["amount"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
                .to_dict("records")
            )

    # Calculate monthly budget analysis
    today = date.today()

    con = get_connection()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                c.category_name,
                mb.budget_amount,
                COALESCE(SUM(t.amount), 0) AS actual_expense
            FROM monthly_budgets mb
            JOIN categories c
                ON mb.category_id = c.category_id
            LEFT JOIN transactions t
                ON t.category_id = mb.category_id
                AND t.transaction_type = 'Expense'
                AND MONTH(t.transaction_date) = mb.budget_month
                AND YEAR(t.transaction_date) = mb.budget_year
            WHERE mb.budget_month = %s
                AND mb.budget_year = %s
            GROUP BY
                c.category_name,
                mb.budget_amount
            ORDER BY c.category_name
        """, (today.month, today.year))

        budget_totals = cursor.fetchall()

    finally:
        cursor.close()
        con.close()

    # Get categories for the transaction form
    categories = get_categories()

    # Display the external HTML template
    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expenses=expenses,
        categories=categories,
        category_totals=category_totals,
        budget_totals=budget_totals,
        error=error,
        today=today.isoformat()
    )


# Generate the expense pie chart
@app.route("/expense-chart")
def expense_chart():
    con = get_connection()
    cursor = con.cursor()

    try:
        cursor.execute("""
            SELECT
                c.category_name,
                SUM(t.amount)
            FROM transactions t
            JOIN categories c
                ON t.category_id = c.category_id
            WHERE t.transaction_type = 'Expense'
            GROUP BY c.category_name
            ORDER BY SUM(t.amount) DESC
        """)

        rows = cursor.fetchall()

    finally:
        cursor.close()
        con.close()

    fig, ax = plt.subplots(figsize=(7, 5))

    if rows:
        ax.pie(
            [float(row[1]) for row in rows],
            labels=[row[0] for row in rows],
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title("Expense Distribution by Category")

    else:
        ax.text(
            0.5, 0.5,
            "No expenses recorded yet",
            ha="center",
            va="center"
        )

        ax.axis("off")

    output = BytesIO()

    fig.tight_layout()
    fig.savefig(output, format="png")
    plt.close(fig)

    output.seek(0)

    return send_file(output, mimetype="image/png")


@app.route("/add-transaction")
def add_transaction():
    categories = get_categories()
    today = date.today()

    return render_template(
        "add_transaction.html",
        categories=categories,
        today=today.isoformat()
    )


@app.route("/analysis")
def analysis():
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.category_name,
                   SUM(t.amount) AS amount
            FROM transactions t
            JOIN categories c
                ON t.category_id = c.category_id
            WHERE t.transaction_type = 'Expense'
            GROUP BY c.category_name
            ORDER BY amount DESC
        """)

        category_totals = cursor.fetchall()

    finally:
        cursor.close()
        con.close()

    return render_template(
        "analysis.html",
        category_totals=category_totals
    )


@app.route("/budget")
def budget():
    today = date.today()
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.category_name,
                   mb.budget_amount,
                   COALESCE(SUM(t.amount), 0) AS actual_expense
            FROM monthly_budgets mb
            JOIN categories c
                ON mb.category_id = c.category_id
            LEFT JOIN transactions t
                ON t.category_id = mb.category_id
                AND t.transaction_type = 'Expense'
                AND MONTH(t.transaction_date) = mb.budget_month
                AND YEAR(t.transaction_date) = mb.budget_year
            WHERE mb.budget_month = %s
                AND mb.budget_year = %s
            GROUP BY c.category_name, mb.budget_amount
            ORDER BY c.category_name
        """, (today.month, today.year))

        budget_totals = cursor.fetchall()

    finally:
        cursor.close()
        con.close()

    return render_template(
        "budget.html",
        budget_totals=budget_totals
    )


@app.route("/transactions")
def transactions():
    con = get_connection()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT t.transaction_id,
                   t.transaction_date,
                   t.transaction_type,
                   c.category_name,
                   t.amount,
                   t.description
            FROM transactions t
            JOIN categories c
                ON t.category_id = c.category_id
            ORDER BY t.transaction_date DESC,
                     t.transaction_id DESC
        """)

        all_transactions = cursor.fetchall()

    finally:
        cursor.close()
        con.close()

    return render_template(
        "transactions.html",
        transactions=all_transactions
    )


if __name__ == "__main__":
    app.run(debug=True)

