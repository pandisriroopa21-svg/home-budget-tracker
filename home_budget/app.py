from flask import Flask, request, redirect
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import config
from datetime import date
from math import isfinite
from markupsafe import escape

app = Flask(__name__)
CHART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
os.makedirs(CHART_DIR, exist_ok=True)


def connect_db():
    return config.connect()


def get_data(query, values=()):
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute(query, values)
        return cursor.fetchall()
    finally:
        cursor.close()
        db.close()


def page(title, content):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
body{{font-family:Arial,sans-serif;background:#f4f6f9;margin:0;color:#263238}}
nav{{background:#2563eb;padding:20px}}
nav a{{color:white;text-decoration:none;margin:10px;font-weight:bold;display:inline-block}}
main{{max-width:1100px;margin:auto;padding:30px}}
h1{{color:#1e40af}}
.card{{display:inline-block;background:white;padding:25px;margin:10px;border-radius:10px;box-shadow:0 2px 6px #ddd}}
.box{{background:white;padding:25px;margin-top:20px;border-radius:10px}}
input,select{{padding:10px;margin:10px;border:1px solid #ccc;border-radius:5px}}
button{{background:#2563eb;color:white;padding:12px 20px;border:0;border-radius:5px;cursor:pointer}}
table{{border-collapse:collapse;width:100%;background:white;margin-top:20px}}
th,td{{border:1px solid #ddd;padding:12px;text-align:left}}
th{{background:#dbeafe}}
img{{max-width:100%}}.danger{{color:red}}.success{{color:green}}
</style></head><body>
<nav><a href="/">Home</a><a href="/dashboard">Dashboard</a><a href="/categories">Categories</a>
<a href="/add">Add Transaction</a><a href="/transactions">Transactions</a>
<a href="/analysis">Analysis</a><a href="/budget">Budget</a></nav>
<main><h1>{escape(title)}</h1>{content}</main></body></html>'''


@app.route('/')
def title():
    return page('Home Budget Tracker', '''<div class="box">
<h2>Welcome to Home Budget Tracker</h2>
<p>Manage income, expenses, savings and monthly budgets.</p>
<p>Analyze spending using Pandas, NumPy and Matplotlib.</p>
<a href="/dashboard">View Dashboard</a></div>''')


def get_categories():
    return get_data('SELECT category_id, category_name, category_type FROM categories ORDER BY category_name')


@app.route('/categories')
def categories_page():
    rows = get_categories()
    content = '<table><tr><th>ID</th><th>Category</th><th>Type</th></tr>'
    for category_id, name, category_type in rows:
        content += f'<tr><td>{category_id}</td><td>{escape(name)}</td><td>{escape(category_type)}</td></tr>'
    content += '</table>'
    if not rows:
        content += '<p>No categories found.</p>'
    return page('Categories', content)


@app.route('/dashboard')
def dashboard():
    rows = get_data('SELECT transaction_type, amount FROM transactions')
    df = pd.DataFrame(rows, columns=['type', 'amount'])
    income = 0.0
    expenses = 0.0
    if not df.empty:
        df['amount'] = pd.to_numeric(df['amount'])
        income = float(df[df['type'] == 'Income']['amount'].sum())
        expenses = float(df[df['type'] == 'Expense']['amount'].sum())
    savings = income - expenses
    create_pie_chart()
    create_monthly_chart()
    content = f'''<div class="card"><h3>Total Income</h3><h2>₹{income:,.2f}</h2></div>
<div class="card"><h3>Total Expenses</h3><h2>₹{expenses:,.2f}</h2></div>
<div class="card"><h3>Total Savings</h3><h2>₹{savings:,.2f}</h2></div>
<div class="box"><h2>Expense Pie Chart</h2><img src="/static/pie_chart.png" width="500"></div>
<div class="box"><h2>Monthly Expense Bar Graph</h2><img src="/static/monthly_chart.png" width="600"></div>'''
    return page('Home Budget Dashboard', content)


@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        transaction_date = request.form.get('transaction_date', '')
        transaction_type = request.form.get('transaction_type', '')
        category_text = request.form.get('category_id', '')
        amount_text = request.form.get('amount', '')
        description = request.form.get('description', '')
        try:
            amount = float(amount_text)
            category_id = int(category_text)
            selected_date = date.fromisoformat(transaction_date)
            if not isfinite(amount) or amount <= 0:
                raise ValueError
            if selected_date > date.today():
                raise ValueError
            if transaction_type not in ('Income', 'Expense'):
                raise ValueError
        except (ValueError, TypeError):
            return page('Invalid Transaction', '<p>Please enter valid details.</p><a href="/add">Try Again</a>'), 400
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT category_type FROM categories WHERE category_id = %s', (category_id,))
            category = cursor.fetchone()
            if category is None or category[0] != transaction_type:
                return page('Invalid Category', '<p>Choose a matching category.</p><a href="/add">Try Again</a>'), 400
            cursor.execute('''INSERT INTO transactions
                (transaction_date, transaction_type, category_id, amount, description)
                VALUES (%s, %s, %s, %s, %s)''',
                (transaction_date, transaction_type, category_id, round(amount, 2), description))
            db.commit()
        except mysql.connector.Error:
            db.rollback()
            return page('Database Error', '<p>Unable to save transaction.</p><a href="/add">Try Again</a>'), 500
        finally:
            cursor.close()
            db.close()
        return redirect('/transactions')

    options = ''
    for category_id, name, category_type in get_categories():
        options += f'<option value="{category_id}">{escape(name)} ({escape(category_type)})</option>'
    content = f'''<div class="box"><form method="POST">
<label>Date:</label><input type="date" name="transaction_date" value="{date.today()}" max="{date.today()}" required><br>
<label>Type:</label><select name="transaction_type" required>
<option value="Income">Income</option><option value="Expense">Expense</option></select><br>
<label>Category:</label><select name="category_id" required>{options}</select><br>
<label>Amount:</label><input type="number" name="amount" min="0.01" step="0.01" required><br>
<label>Description:</label><input type="text" name="description" maxlength="255"><br>
<button type="submit">Add Transaction</button></form></div>'''
    return page('Add Transaction', content)


@app.route('/transactions')
def transactions():
    rows = get_data('''SELECT t.transaction_date, t.transaction_type, c.category_name,
        t.amount, t.description FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        ORDER BY t.transaction_date DESC, t.transaction_id DESC''')
    content = '<table><tr><th>Date</th><th>Type</th><th>Category</th><th>Amount</th><th>Description</th></tr>'
    for row in rows:
        content += '<tr>'
        for value in row:
            content += f'<td>{escape(str(value if value is not None else ""))}</td>'
        content += '</tr>'
    content += '</table>'
    if not rows:
        content += '<p>No transactions recorded yet.</p>'
    return page('Transaction History', content)


@app.route('/analysis')
def analysis():
    rows = get_data('''SELECT c.category_name, SUM(t.amount) FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.transaction_type = 'Expense'
        GROUP BY c.category_id, c.category_name ORDER BY SUM(t.amount) DESC''')
    content = '<h2>Category-wise Expense Analysis</h2>'
    if rows:
        categories = [row[0] for row in rows]
        amounts = np.array([float(row[1]) for row in rows])
        total = np.sum(amounts)
        average = np.mean(amounts)
        highest = np.max(amounts)
        lowest = np.min(amounts)
        for label, value in [('Total Expenses', total), ('Average Spending', average),
                             ('Highest Spending', highest), ('Lowest Spending', lowest)]:
            content += f'<div class="card"><h3>{label}</h3><h2>₹{value:,.2f}</h2></div>'
        df = pd.DataFrame({'Category': categories, 'Amount': amounts})
        content += '<table><tr><th>Category</th><th>Amount</th></tr>'
        for _, row in df.iterrows():
            content += f'<tr><td>{escape(str(row["Category"]))}</td><td>₹{row["Amount"]:,.2f}</td></tr>'
        content += '</table>'
    else:
        content += '<p>No expenses recorded yet.</p>'
    create_pie_chart()
    create_monthly_chart()
    content += '''<div class="box"><h2>Expense Pie Chart</h2>
<img src="/static/pie_chart.png" width="500"></div>
<div class="box"><h2>Monthly Expense Bar Graph</h2>
<img src="/static/monthly_chart.png" width="600"></div>'''
    return page('Expense Analysis', content)


def create_pie_chart():
    rows = get_data('''SELECT c.category_name, SUM(t.amount) FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.transaction_type = 'Expense'
        GROUP BY c.category_id, c.category_name''')
    fig, ax = plt.subplots(figsize=(7, 5))
    if rows:
        labels = [row[0] for row in rows]
        amounts = [float(row[1]) for row in rows]
        ax.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('Expense Distribution by Category')
    else:
        ax.text(0.5, 0.5, 'No expenses recorded', ha='center', va='center')
        ax.axis('off')
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, 'pie_chart.png'))
    plt.close(fig)


def create_monthly_chart():
    rows = get_data('''SELECT DATE_FORMAT(transaction_date, '%Y-%m'), SUM(amount)
        FROM transactions WHERE transaction_type = 'Expense'
        GROUP BY DATE_FORMAT(transaction_date, '%Y-%m')
        ORDER BY DATE_FORMAT(transaction_date, '%Y-%m')''')
    fig, ax = plt.subplots(figsize=(8, 5))
    if rows:
        months = [row[0] for row in rows]
        amounts = [float(row[1]) for row in rows]
        ax.bar(months, amounts)
        ax.set_title('Monthly Expense Analysis')
        ax.set_xlabel('Month')
        ax.set_ylabel('Expenses (INR)')
        ax.tick_params(axis='x', rotation=45)
    else:
        ax.text(0.5, 0.5, 'No monthly expenses', ha='center', va='center')
        ax.axis('off')
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, 'monthly_chart.png'))
    plt.close(fig)


@app.route('/chart')
def chart():
    create_pie_chart()
    return redirect('/static/pie_chart.png')


@app.route('/monthly-chart')
def monthly_chart():
    create_monthly_chart()
    return redirect('/static/monthly_chart.png')


@app.route('/budget')
def budget():
    rows = get_data('''SELECT c.category_name, m.budget_amount, COALESCE(SUM(t.amount), 0)
        FROM monthly_budgets m JOIN categories c ON m.category_id = c.category_id
        LEFT JOIN transactions t ON t.category_id = m.category_id
            AND t.transaction_type = 'Expense'
            AND MONTH(t.transaction_date) = m.budget_month
            AND YEAR(t.transaction_date) = m.budget_year
        WHERE m.budget_month = MONTH(CURDATE()) AND m.budget_year = YEAR(CURDATE())
        GROUP BY m.budget_id, c.category_name, m.budget_amount
        ORDER BY c.category_name''')
    content = '''<h2>Current Month Budget Report</h2><table><tr>
<th>Category</th><th>Budget</th><th>Spent</th><th>Remaining</th><th>Status</th></tr>'''
    for category, budget_amount, spent in rows:
        remaining = budget_amount - spent
        status = ('<span class="danger">Over Budget</span>' if spent > budget_amount
                  else '<span class="success">Within Budget</span>')
        content += f'''<tr><td>{escape(category)}</td><td>₹{float(budget_amount):,.2f}</td>
<td>₹{float(spent):,.2f}</td><td>₹{float(remaining):,.2f}</td><td>{status}</td></tr>'''
    content += '</table>'
    if not rows:
        content += '<p>No budgets found for this month.</p>'
    return page('Monthly Budget Analysis', content)


if __name__ == '__main__':
    app.run(debug=True)
