import pandas as pd
import numpy as np
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

print("CATEGORY-WISE EXPENSES")
print(category_expenses)

print("\nTotal Expenses: Rs.", total_expenses)

# Create Bar Chart
plt.figure(figsize=(10, 6))

plt.bar(
    category_expenses.index,
    category_expenses.values,
    color="skyblue",
    edgecolor="black"
)

plt.title("Category-wise Expenses - Home Budget")
plt.xlabel("Expense Categories")
plt.ylabel("Amount (INR)")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

# Save chart inside static folder
plt.savefig(STATIC_DIR / "category_expenses.png", dpi=150)

plt.show()
plt.close()

print("\nCategory Expenses Chart Created Successfully!")
