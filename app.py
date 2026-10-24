

from flask import Flask, render_template_string, send_file
import mysql.connector
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("DB_PASSWORD"),
        database="home_budget_db"
    )


def get_transactions():
    con = get_connection()
    cursor = con.cursor(dictionary=True)

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
        ORDER BY t.transaction_date DESC
    """)

    transactions = cursor.fetchall()
    cursor.close()
    con.close()
    return transactions


@app.route("/")
def home():
    transactions = get_transactions()
    df = pd.DataFrame(transactions)

    income = 0
    expenses = 0
    category_expenses = []

    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"])

        income = float(
            df.loc[df["transaction_type"] == "Income", "amount"].sum()
        )
        expenses = float(
            df.loc[df["transaction_type"] == "Expense", "amount"].sum()
        )

        expense_df = df[df["transaction_type"] == "Expense"]

        if not expense_df.empty:
            grouped = (
                expense_df.groupby("category_name")["amount"]
                .sum()
                .sort_values(ascending=False)
            )

            category_expenses = [
                {"category": category, "amount": float(amount)}
                for category, amount in grouped.items()
            ]

    balance = income - expenses

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home Budget Tracker</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f1f5f9;
                margin: 0;
                padding: 30px;
                color: #1e293b;
            }
            h1, .subtitle { text-align: center; }
            .cards {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
                margin: 25px 0;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 12px;
                min-width: 190px;
                box-shadow: 0 3px 12px #0001;
            }
            .income { color: #15803d; }
            .expense { color: #dc2626; }
            .balance { color: #1d4ed8; }
            .section {
                background: white;
                padding: 20px;
                margin: 22px 0;
                border-radius: 12px;
                box-shadow: 0 3px 12px #0001;
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                border-bottom: 1px solid #e2e8f0;
                text-align: left;
            }
            th { background: #e2e8f0; }
            .chart {
                display: block;
                max-width: 100%;
                width: 650px;
                margin: auto;
            }
        </style>
    </head>
    <body>
        <h1>Home Budget Tracker</h1>
        <p class="subtitle">Track your income, expenses and savings</p>

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
                <h2 class="balance">₹{{ "%.2f"|format(balance) }}</h2>
            </div>
        </div>

        <div class="section">
            <h2>Category-wise Expense Analysis</h2>
            {% if category_expenses %}
            <table>
                <tr>
                    <th>Category</th>
                    <th>Total Expense (₹)</th>
                </tr>
                {% for item in category_expenses %}
                <tr>
                    <td>{{ item.category }}</td>
                    <td>{{ "%.2f"|format(item.amount) }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p>No expense data available yet.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>Expense Distribution Pie Chart</h2>
            {% if category_expenses %}
            <img class="chart" src="/expense-chart"
                 alt="Category-wise expense pie chart">
            {% else %}
            <p>Add expense transactions to display a chart.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>Transaction History</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Amount (₹)</th>
                    <th>Description</th>
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
    </body>
    </html>
    """, transactions=transactions, income=income,
         expenses=expenses, balance=balance,
         category_expenses=category_expenses)


@app.route("/expense-chart")
def expense_chart():
    transactions = get_transactions()
    df = pd.DataFrame(transactions)

    image = BytesIO()

    if df.empty:
        plt.figure()
        plt.text(0.5, 0.5, "No transaction data",
                 ha="center", va="center")
        plt.axis("off")
    else:
        df["amount"] = pd.to_numeric(df["amount"])
        expense_df = df[df["transaction_type"] == "Expense"]

        if expense_df.empty:
            plt.figure()
            plt.text(0.5, 0.5, "No expenses to display",
                     ha="center", va="center")
            plt.axis("off")
        else:
            category_totals = expense_df.groupby(
                "category_name"
            )["amount"].sum()

            plt.figure(figsize=(8, 6))
            plt.pie(
                category_totals.values,
                labels=category_totals.index,
                autopct="%1.1f%%",
                startangle=90
            )
            plt.title("Expenses by Category")
            plt.axis("equal")

    plt.tight_layout()
    plt.savefig(image, format="png", bbox_inches="tight")
    plt.close()
    image.seek(0)

    return send_file(image, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)


