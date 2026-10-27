from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import pandas as pd
import numpy as np


app = Flask(__name__)
def db():
    return mysql.connector.connect(
        host='localhost', user='root',
        password='YOUR_MYSQL_PASSWORD', database='home_budget'
    )
def query(sql, params=(), fetch=True):
    conn = db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        result = cur.fetchall() if fetch else None
        if not fetch:
            conn.commit()
        return result
    finally:
        cur.close()
        conn.close()
@app.route('/')
def dashboard():
    rows = query('SELECT transaction_type, amount FROM transactions')
    df = pd.DataFrame(rows)
    if df.empty:
        income = expense = 0.0
    else:
        df['amount'] = df['amount'].astype(float)
        income = float(df.loc[
            df.transaction_type == 'income', 'amount'].sum())
        expense = float(df.loc[
            df.transaction_type == 'expense', 'amount'].sum())
    savings = float(np.subtract(income, expense))
    return render_template('dashboard.html',
                           income=income, expense=expense,
                           savings=savings)
@app.route('/transactions')
def transactions():
    rows = query('''SELECT t.transaction_id,t.transaction_date,
      t.transaction_type,t.amount,t.description,c.category_name
      FROM transactions t JOIN categories c
      ON t.category_id=c.category_id
      ORDER BY t.transaction_date DESC''')
    return render_template('transactions.html', rows=rows)
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        if amount <= 0:
            return 'Amount must be positive', 400
        query('''INSERT INTO transactions
          (transaction_date,transaction_type,category_id,
           amount,description) VALUES (%s,%s,%s,%s,%s)''',
          (request.form['date'],request.form['type'],
           int(request.form['category_id']),amount,
           request.form.get('description','')), fetch=False)
        return redirect(url_for('transactions'))
    cats = query('SELECT * FROM categories ORDER BY category_name')
    return render_template('add.html', categories=cats)
@app.post('/delete/<int:transaction_id>')
def delete(transaction_id):
    query('DELETE FROM transactions WHERE transaction_id=%s',
          (transaction_id,), fetch=False)
    return redirect(url_for('transactions'))
if __name__ == '__main__':

    app.run(debug=True)
