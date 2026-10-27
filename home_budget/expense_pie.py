import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


data = {
    "category": [
        "Rent",
        "Groceries",
        "Transportation",
        "Education",
        "Entertainment",
        "Healthcare"
    ],
    "amount": [
        12000,
        4500,
        1500,
        3000,
        1000,
        2000
    ]
}


df = pd.DataFrame(data)


category_expenses = df.groupby("category")["amount"].sum()


total_expenses = np.sum(category_expenses.values)

print("EXPENSE DISTRIBUTION")
print("---------------------------")
print(category_expenses)
print("\nTotal Expenses: Rs.", total_expenses)


plt.figure(figsize=(9, 7))

plt.pie(
    category_expenses.values,
    labels=category_expenses.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Home Budget - Expense Distribution")

plt.tight_layout()

plt.savefig(
    STATIC_DIR / "expense_pie.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("\nExpense Pie Chart Created Successfully!")
print("Saved in:", STATIC_DIR / "expense_pie.png")
