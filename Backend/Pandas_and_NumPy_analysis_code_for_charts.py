
import os
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt



data = {
    "transaction_date": [
        "2026-09-01",
        "2026-09-05",
        "2026-09-10",
        "2026-10-01",
        "2026-10-02",
        "2026-10-03",
        "2026-10-04",
        "2026-10-05",
        "2026-10-06"
    ],

    "transaction_type": [
        "Income",
        "Expense",
        "Expense",
        "Income",
        "Expense",
        "Expense",
        "Expense",
        "Expense",
        "Expense"
    ],

    "category_name": [
        "Salary",
        "Rent",
        "Groceries",
        "Salary",
        "Rent",
        "Groceries",
        "Transportation",
        "Education",
        "Entertainment"
    ],

    "amount": [
        45000,
        10000,
        4000,
        50000,
        12000,
        4500,
        1500,
        3000,
        1000
    ]
}

# Create Pandas DataFrame
df = pd.DataFrame(data)

print("\nHOME BUDGET TRANSACTIONS")
print(df)




BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(STATIC_DIR, exist_ok=True)


def save_chart(filename):
    filepath = os.path.join(STATIC_DIR, filename)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close()

    print("Saved:", filepath)



df["transaction_date"] = pd.to_datetime(
    df["transaction_date"]
)

df["amount"] = pd.to_numeric(df["amount"])

df["month"] = df["transaction_date"].dt.strftime("%Y-%m")

df["transaction_type"] = (
    df["transaction_type"].str.lower()
)


october = df[df["month"] == "2026-10"]

income = october[
    october["transaction_type"] == "income"
]["amount"].sum()

expenses = october[
    october["transaction_type"] == "expense"
]["amount"].sum()


savings = np.subtract(income, expenses)

print("\nFINANCIAL SUMMARY")
print("-----------------------------")
print("Total Income: Rs.", income)
print("Total Expenses: Rs.", expenses)
print("Total Savings: Rs.", savings)



expense_data = october[
    october["transaction_type"] == "expense"
]

category_totals = expense_data.groupby(
    "category_name"
)["amount"].sum()

print("\nCATEGORY-WISE EXPENSES")
print(category_totals)



plt.figure(figsize=(9, 5))

plt.bar(
    category_totals.index,
    category_totals.values,
    color="skyblue"
)

plt.title("Category-wise Expenses")
plt.xlabel("Category")
plt.ylabel("Amount (INR)")
plt.xticks(rotation=45, ha="right")

save_chart("category_expenses.png")



plt.figure(figsize=(8, 6))

plt.pie(
    category_totals.values,
    labels=category_totals.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Expense Distribution")

save_chart("expense_pie.png")



monthly = df.groupby(
    ["month", "transaction_type"]
)["amount"].sum().unstack(fill_value=0)

monthly = monthly.reindex(
    columns=["income", "expense"],
    fill_value=0
)

plt.figure(figsize=(9, 5))

plt.plot(
    monthly.index,
    monthly["income"],
    marker="o",
    label="Income",
    color="green"
)

plt.plot(
    monthly.index,
    monthly["expense"],
    marker="o",
    label="Expenses",
    color="red"
)

plt.title("Monthly Income vs Expenses")
plt.xlabel("Month")
plt.ylabel("Amount (INR)")
plt.legend()
plt.grid(True)

save_chart("monthly_comparison.png")



budget = {
    "Rent": 10000,
    "Groceries": 6000,
    "Transportation": 3000,
    "Education": 4000,
    "Entertainment": 2000
}

categories = list(budget.keys())

budget_amounts = np.array(
    list(budget.values()),
    dtype=float
)

actual_amounts = np.array(
    [
        category_totals.get(category, 0)
        for category in categories
    ],
    dtype=float
)

utilization = np.divide(
    actual_amounts,
    budget_amounts,
    out=np.zeros_like(actual_amounts),
    where=budget_amounts != 0
) * 100

print("\nBUDGET UTILIZATION")
print("-----------------------------")

for i in range(len(categories)):

    print("\nCategory:", categories[i])
    print("Budget: Rs.", budget_amounts[i])
    print("Spent: Rs.", actual_amounts[i])
    print("Utilization:", round(utilization[i], 2), "%")

    if actual_amounts[i] > budget_amounts[i]:

        print(
            "OVER BUDGET BY Rs.",
            actual_amounts[i] - budget_amounts[i]
        )

    else:

        print(
            "Remaining Budget: Rs.",
            budget_amounts[i] - actual_amounts[i]
        )



x = np.arange(len(categories))

width = 0.35

plt.figure(figsize=(10, 5))

plt.bar(
    x - width / 2,
    budget_amounts,
    width,
    label="Budget",
    color="blue"
)

plt.bar(
    x + width / 2,
    actual_amounts,
    width,
    label="Actual Expenses",
    color="orange"
)

plt.xticks(
    x,
    categories,
    rotation=45,
    ha="right"
)

plt.xlabel("Category")
plt.ylabel("Amount (INR)")
plt.title("Budget vs Actual Expenses")
plt.legend()

save_chart("budget_comparison.png")



print("\n===================================")
print("HOME BUDGET ANALYSIS COMPLETED")
print("===================================")

print("All 4 charts generated successfully!")
print("Check your static folder.")
