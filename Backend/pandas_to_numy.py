import mysql.connector
import pandas as pd
import numpy as np

conn = mysql.connector.connect(
host='localhost', user='root',
password='YOUR_PASSWORD', database='home_budget'
)
cursor = conn.cursor(dictionary=True)
cursor.execute('''
SELECT t.transaction_date, t.transaction_type,
c.category_name, t.amount
FROM transactions t JOIN categories c
ON t.category_id = c.category_id
''')
df = pd.DataFrame(cursor.fetchall())
cursor.close()
conn.close()
df['amount'] = pd.to_numeric(df['amount'])
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
df['month'] = df['transaction_date'].dt.strftime('%Y-%m')
monthly = df.pivot_table(
index='month', columns='transaction_type',
values='amount', aggfunc='sum', fill_value=0
)
for col in ['income', 'expense']:
 if col not in monthly: monthly[col] = 0
monthly['savings'] = np.subtract(
monthly['income'], monthly['expense']
)
print(monthly)
