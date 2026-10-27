import os
from datetime import date

import mysql.connector
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt



import os
import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD", "YOUR_PASSWORD"),
        database="home_budget"
    )
    return connection
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD", "YOUR_PASSWORD"),
        database="home_budget"
    )




def get_transactions():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
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
        ORDER BY t.transaction_date
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        columns = [
            "transaction_id",
            "transaction_date",
            "transaction_type",
            "category_name",
            "amount",
            "description"
        ]

        df = pd.DataFrame(rows, columns=columns)

        if not df.empty:
            df["transaction_date"] = pd.to_datetime(
                df["transaction_date"]
            )

            df["amount"] = pd.to_numeric(
                df["amount"]
            )

        return df

    finally:
        cursor.close()
        connection.close()



def get_budgets(month, year):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT
            c.category_name,
            b.budget_amount
        FROM monthly_budgets b
        JOIN categories c
            ON b.category_id = c.category_id
        WHERE b.budget_month = %s
          AND b.budget_year = %s
        """

        cursor.execute(query, (month, year))
        rows = cursor.fetchall()

        df = pd.DataFrame(
            rows,
            columns=["category_name", "budget_amount"]
        )

        if not df.empty:
            df["budget_amount"] = pd.to_numeric(
                df["budget_amount"]
            )

        return df

    finally:
        cursor.close()
        connection.close()



def save_graph(filename):
    static_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "static"
    )

    os.makedirs(static_folder, exist_ok=True)

    filepath = os.path.join(static_folder, filename)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()



def create_empty_graph(title, filename):
    plt.figure(figsize=(8, 5))

    plt.title(title)
    plt.text(
        0.5,
        0.5,
        "No data available",
        ha="center",
        va="center",
        fontsize=14
    )

    plt.axis("off")
    save_graph(filename)


def category_expense_graph(df, month, year):

    expenses = df[
        (df["transaction_type"] == "Expense") &
        (df["transaction_date"].dt.month == month) &
        (df["transaction_date"].dt.year == year)
    ]

    if expenses.empty:
        create_empty_graph(
            "Category-wise Expenses",
            "category_expenses.png"
        )
        return

    category_data = expenses.groupby(
        "category_name"
    )["amount"].sum().sort_values(ascending=False)

    plt.figure(figsize=(9, 5))

    category_data.plot(kind="bar", color="skyblue")

    plt.title(f"Category-wise Expenses - {month}/{year}")
    plt.xlabel("Expense Category")
    plt.ylabel("Amount (INR)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.3)

    save_graph("category_expenses.png")



def monthly_comparison_graph(df, year):

    year_data = df[
        df["transaction_date"].dt.year == year
    ].copy()

    if year_data.empty:
        create_empty_graph(
            "Monthly Income vs Expenses",
            "monthly_comparison.png"
        )
        return

    year_data["month"] = (
        year_data["transaction_date"].dt.month
    )

    monthly = year_data.pivot_table(
        index="month",
        columns="transaction_type",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    monthly = monthly.reindex(
        range(1, 13),
        fill_value=0
    )

    for column in ["Income", "Expense"]:
        if column not in monthly.columns:
            monthly[column] = 0

    x = np.arange(1, 13)
    width = 0.35

    plt.figure(figsize=(10, 5))

    plt.bar(
        x - width / 2,
        monthly["Income"],
        width,
        label="Income",
        color="green"
    )

    plt.bar(
        x + width / 2,
        monthly["Expense"],
        width,
        label="Expenses",
        color="red"
    )

    plt.title(f"Monthly Income vs Expenses - {year}")
    plt.xlabel("Month")
    plt.ylabel("Amount (INR)")
    plt.xticks(x)
    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    save_graph("monthly_comparison.png")


def expense_pie_chart(df, month, year):

    expenses = df[
        (df["transaction_type"] == "Expense") &
        (df["transaction_date"].dt.month == month) &
        (df["transaction_date"].dt.year == year)
    ]

    if expenses.empty:
        create_empty_graph(
            "Expense Distribution",
            "expense_pie.png"
        )
        return

    category_data = expenses.groupby(
        "category_name"
    )["amount"].sum()

    plt.figure(figsize=(8, 6))

    plt.pie(
        category_data.values,
        labels=category_data.index,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title(f"Expense Distribution - {month}/{year}")

    save_graph("expense_pie.png")



def budget_comparison_graph(df, budgets_df, month, year):

    if budgets_df.empty:
        create_empty_graph(
            "Budget vs Actual Expenses",
            "budget_comparison.png"
        )
        return

    expenses = df[
        (df["transaction_type"] == "Expense") &
        (df["transaction_date"].dt.month == month) &
        (df["transaction_date"].dt.year == year)
    ]

    actual = expenses.groupby(
        "category_name"
    )["amount"].sum().reset_index()

    actual.rename(
        columns={"amount": "actual_expense"},
        inplace=True
    )

    comparison = pd.merge(
        budgets_df,
        actual,
        on="category_name",
        how="left"
    )

    comparison["actual_expense"] = (
        comparison["actual_expense"].fillna(0)
    )

    comparison["remaining"] = np.subtract(
        comparison["budget_amount"],
        comparison["actual_expense"]
    )

    comparison["status"] = np.where(
        comparison["remaining"] < 0,
        "Over Budget",
        "Within Budget"
    )

    x = np.arange(len(comparison))
    width = 0.35

    plt.figure(figsize=(10, 5))

    plt.bar(
        x - width / 2,
        comparison["budget_amount"],
        width,
        label="Budget",
        color="blue"
    )

    plt.bar(
        x + width / 2,
        comparison["actual_expense"],
        width,
        label="Actual Expense",
        color="orange"
    )

    plt.title(f"Budget vs Actual Expenses - {month}/{year}")
    plt.xlabel("Category")
    plt.ylabel("Amount (INR)")

    plt.xticks(
        x,
        comparison["category_name"],
        rotation=45,
        ha="right"
    )

    plt.legend()
    plt.grid(axis="y", alpha=0.3)

    save_graph("budget_comparison.png")



def financial_summary(df, month, year):

    monthly_data = df[
        (df["transaction_date"].dt.month == month) &
        (df["transaction_date"].dt.year == year)
    ]

    income = monthly_data[
        monthly_data["transaction_type"] == "Income"
    ]["amount"].sum()

    expenses = monthly_data[
        monthly_data["transaction_type"] == "Expense"
    ]["amount"].sum()

    savings = np.subtract(income, expenses)

    return {
        "income": float(income),
        "expenses": float(expenses),
        "savings": float(savings)
    }


def generate_reports(month=None, year=None):

    today = date.today()

    if month is None:
        month = today.month

    if year is None:
        year = today.year

    df = get_transactions()
    budgets_df = get_budgets(month, year)

    category_expense_graph(df, month, year)

    monthly_comparison_graph(df, year)

    expense_pie_chart(df, month, year)

    budget_comparison_graph(
        df,
        budgets_df,
        month,
        year
    )

    summary = financial_summary(df, month, year)

    return summary



if __name__ == "__main__":

    print("HOME BUDGET ANALYSIS SYSTEM")
    print("---------------------------")

    month = 10
    year = 2026

    summary = generate_reports(month, year)

    print("Month:", month)
    print("Year:", year)

    print("Total Income: Rs.", summary["income"])
    print("Total Expenses: Rs.", summary["expenses"])
    print("Total Savings: Rs.", summary["savings"])

    print("\nFour graphs generated successfully!")
    print("Check the static folder.")
