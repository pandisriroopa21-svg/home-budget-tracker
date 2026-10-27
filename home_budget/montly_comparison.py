

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


data = {
    "month": [
        "2026-08", "2026-08",
        "2026-09", "2026-09",
        "2026-10", "2026-10"
    ],
    "transaction_type": [
        "Income", "Expense",
        "Income", "Expense",
        "Income", "Expense"
    ],
    "amount": [
        40000, 15000,
        45000, 18000,
        50000, 22000
    ]
}


df = pd.DataFrame(data)


df["transaction_type"] = df["transaction_type"].str.lower()


monthly = df.groupby(
    ["month", "transaction_type"]
)["amount"].sum().unstack(fill_value=0)

monthly = monthly.reindex(
    columns=["income", "expense"],
    fill_value=0
)


monthly["savings"] = np.subtract(
    monthly["income"],
    monthly["expense"]
)

print("\nMONTHLY FINANCIAL ANALYSIS")
print("-----------------------------")
print(monthly)

# STEP 6: Create Line Chart
plt.figure(figsize=(10, 6))

plt.plot(
    monthly.index,
    monthly["income"],
    marker="o",
    color="green",
    linewidth=2,
    label="Income"
)

plt.plot(
    monthly.index,
    monthly["expense"],
    marker="o",
    color="red",
    linewidth=2,
    label="Expenses"
)

plt.title("Monthly Income vs Expenses - Home Budget")
plt.xlabel("Month")
plt.ylabel("Amount (INR)")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    STATIC_DIR / "monthly_comparison.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("\nMonthly Comparison Chart Created Successfully!")
print("Saved in:", STATIC_DIR / "monthly_comparison.png")
