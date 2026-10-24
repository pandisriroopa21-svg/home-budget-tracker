
from flask import Flask, render_template_string
import mysql.connector
import os

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("DB_PASSWORD"),
     database="home_budget_db"
    )

@app.route("/")
def home():
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

    return render_template_string("""
        <h1>Home Budget Tracker</h1>
        <table border="1" cellpadding="8">
            <tr>
                <th>ID</th>
                <th>Date</th>
                <th>Type</th>
                <th>Category</th>
                <th>Amount</th>
                <th>Description</th>
            </tr>
            {% for t in transactions %}
            <tr>
                <td>{{ t.transaction_id }}</td>
                <td>{{ t.transaction_date }}</td>
                <td>{{ t.transaction_type }}</td>
                <td>{{ t.category_name }}</td>
                <td>{{ t.amount }}</td>
                <td>{{ t.description or '' }}</td>
            </tr>
            {% endfor %}
        </table>
    """, transactions=transactions)

if __name__ == "__main__":
    app.run(debug=True)
