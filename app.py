
from flask import Flask, render_template_string, request, redirect, url_for, send_file
import mysql.connector
import os
import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import date
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("DB_PASSWORD"),
        database="home_budget_db"
    )

def get_categories():
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT category_id, category_name FROM categories ORDER BY category_name"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        con.close()

@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        transaction_type = request.form.get("transaction_type", "")
        category_text = request.form.get("category_id", "")
        amount_text = request.form.get("amount", "").strip()
        transaction_date = request.form.get("transaction_date", "")
        description = request.form.get("description", "").strip()

        category_id = None
        try:
            category_id = int(category_text)
        except (ValueError, TypeError):
            error = "Please select a valid category."

        amount = None
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
        except ValueError:
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
                        (transaction_date, transaction_type, category_id,
                         amount, description)
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
                error = "Unable to save transaction. Check the database connection."
            finally:
                if cursor:
                    cursor.close()
                if con and con.is_connected():
                    con.close()

            if not error:
                return redirect(url_for("home", added="1"))

    con = get_connection()
    cursor = con.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT t.transaction_id, t.transaction_date,
                   t.transaction_type, c.category_name,
                   t.amount, t.description
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            ORDER BY t.transaction_date DESC, t.transaction_id DESC
        """)
        transactions = cursor.fetchall()
    finally:
        cursor.close()
        con.close()

    df = pd.DataFrame(transactions)
    income = 0.0
    expenses = 0.0
    category_totals = []

    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"])
        income = float(df.loc[
            df["transaction_type"] == "Income", "amount"
        ].sum())
        expenses = float(df.loc[
            df["transaction_type"] == "Expense", "amount"
        ].sum())

        expense_df = df[df["transaction_type"] == "Expense"]
        if not expense_df.empty:
            category_totals = (
                expense_df.groupby("category_name")["amount"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
                .to_dict("records")
            )

    categories = get_categories()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Home Budget Tracker</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f1f5f9;
                color: #1e293b;
                margin: 0;
                padding: 25px;
            }
            .container { max-width: 1100px; margin: auto; }
            h1 { text-align: center; }
            .cards {
                display: flex; gap: 18px; justify-content: center;
                flex-wrap: wrap; margin: 25px 0;
            }
            .card, .panel {
                background: white; padding: 22px; border-radius: 12px;
                box-shadow: 0 3px 12px #0001; margin-bottom: 22px;
            }
            .card { min-width: 190px; }
            .income { color: #15803d; }
            .expense { color: #dc2626; }
            .balance { color: #1d4ed8; }
            .form-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 16px;
            }
            label { display: block; font-weight: bold; margin-bottom: 7px; }
            input, select {
                box-sizing: border-box; width: 100%; padding: 11px;
                border: 1px solid #cbd5e1; border-radius: 7px;
                font-size: 15px;
            }
            button {
                margin-top: 18px; padding: 12px 22px; border: 0;
                border-radius: 7px; background: #2563eb; color: white;
                font-size: 16px; cursor: pointer;
            }
            .table-box { overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; }
            th, td {
                padding: 12px; border-bottom: 1px solid #e2e8f0;
                text-align: left;
            }
            th { background: #e2e8f0; }
            .message, .error { padding: 12px; border-radius: 7px; }
            .message { background: #dcfce7; color: #166534; }
            .error { background: #fee2e2; color: #991b1b; }
        </style>
    </head>
    <body>
    <div class="container">
        <h1>Home Budget Tracker</h1>
        <p style="text-align:center">Track your income, expenses and savings</p>

        {% if request.args.get('added') %}
            <p class="message">Transaction added successfully!</p>
        {% endif %}
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        <div class="cards">
            <div class="card">
                <h3>Total Income</h3>
                <h2 class="income">₹{{ "%.2f"|format(income) }}</h2>
            </div>
            <div class="card">
                <h3>Total Expenses</h3>
                <h2 class="expense">₹{{ "%.2f"|format(expenses) }}</h2>
            </div>
            <div class="card">
                <h3>Remaining Balance</h3>
                <h2 class="balance">₹{{ "%.2f"|format(income - expenses) }}</h2>
            </div>
        </div>

        <div class="panel">
            <h2>Add Income / Expense</h2>
            <form method="POST">
                <div class="form-grid">
                    <div>
                        <label for="transaction_type">Transaction Type</label>
                        <select id="transaction_type" name="transaction_type" required>
                            <option value="">Select type</option>
                            <option value="Income">Income</option>
                            <option value="Expense">Expense</option>
                        </select>
                    </div>
                    <div>
                        <label for="category_id">Category</label>
                        <select id="category_id" name="category_id" required>
                            <option value="">Select category</option>
                            {% for c in categories %}
                            <option value="{{ c.category_id }}">{{ c.category_name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div>
                        <label for="amount">Amount (₹)</label>
                        <input id="amount" name="amount" type="number"
                               min="0.01" step="0.01" required>
                    </div>
                    <div>
                        <label for="transaction_date">Date</label>
                        <input id="transaction_date" name="transaction_date"
                               type="date" max="{{ today }}" value="{{ today }}" required>
                    </div>
                    <div>
                        <label for="description">Description</label>
                        <input id="description" name="description" type="text"
                               maxlength="255" placeholder="e.g. Monthly salary">
                    </div>
                </div>
                <button type="submit">Add Transaction</button>
            </form>
        </div>

        <div class="panel">
            <h2>Category-wise Expense Analysis</h2>
            {% if category_totals %}
            <div class="table-box">
                <table>
                    <tr><th>Category</th><th>Total Expense (₹)</th></tr>
                    {% for item in category_totals %}
                    <tr>
                        <td>{{ item.category_name }}</td>
                        <td>{{ "%.2f"|format(item.amount|float) }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            {% else %}
            <p>No expenses recorded yet.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h2>Expense Distribution Pie Chart</h2>
            <img src="/expense-chart" alt="Expense pie chart"
                 style="max-width:100%;width:500px">
        </div>

        <div class="panel table-box">
            <h2>Transaction History</h2>
            <table>
                <tr>
                    <th>ID</th><th>Date</th><th>Type</th><th>Category</th>
                    <th>Amount (₹)</th><th>Description</th>
                </tr>
                {% for t in transactions %}
                <tr>
                    <td>{{ t.transaction_id }}</td>
                    <td>{{ t.transaction_date }}</td>
                    <td>{{ t.transaction_type }}</td>
                    <td>{{ t.category_name }}</td>
                    <td>{{ "%.2f"|format(t.amount|float) }}</td>
                    <td>{{ t.description or "" }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
    </body>
    </html>
    """, transactions=transactions, income=income, expenses=expenses,
         categories=categories, category_totals=category_totals,
         error=error, today=date.today().isoformat())


@app.route("/expense-chart")
def expense_chart():
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("""
            SELECT c.category_name, SUM(t.amount)
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
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
        ax.text(0.5, 0.5, "No expenses recorded yet",
                ha="center", va="center")
        ax.axis("off")

    output = BytesIO()
    fig.tight_layout()
    fig.savefig(output, format="png")
    plt.close(fig)
    output.seek(0)
    return send_file(output, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
