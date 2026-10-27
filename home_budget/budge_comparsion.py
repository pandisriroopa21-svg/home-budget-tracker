from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


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
    "budget": [
        10000,
        6000,
        3000,
        4000,
        2000,
        3000
    ],
    "actual_expenses": [
        12000,
        4500,
        1500,
        3000,
        1000,
        2000
    ]
}


df = pd.DataFrame(data)


df["remaining_budget"] = np.subtract(
    df["budget"],
    df["actual_expenses"]
)


df["utilization"] = np.divide(
    df["actual_expenses"],
    df["budget"]
) * 100

print("\nHOME BUDGET ANALYSIS")
print("--------------------------------")

print(df)


print("\nBUDGET STATUS")
print("--------------------------------")

for _, row in df.iterrows():

    category = row["category"]
    budget = row["budget"]
    spent = row["actual_expenses"]

    if spent > budget:
        print(
            category,
            "- OVER BUDGET BY Rs.",
            spent - budget
        )
    else:
        print(
            category,
            "- Remaining Rs.",
            budget - spent
        )


x = np.arange(len(df))
width = 0.35

plt.figure(figsize=(11, 6))

plt.bar(
    x - width / 2,
    df["budget"],
    width,
    label="Budget",
    color="royalblue"
)

plt.bar(
    x + width / 2,
    df["actual_expenses"],
    width,
    label="Actual Expenses",
    color="orange"
)

plt.xticks(
    x,
    df["category"],
    rotation=45,
    ha="right"
)

plt.title("Budget vs Actual Expenses - Home Budget")
plt.xlabel("Expense Categories")
plt.ylabel("Amount (INR)")
plt.legend()
plt.grid(axis="y", alpha=0.3)


plt.tight_layout()

plt.savefig(
    STATIC_DIR / "budget_comparison.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("\nBudget Comparison Chart Created Successfully!")
print("Saved in:", STATIC_DIR / "budget_comparison.png")
