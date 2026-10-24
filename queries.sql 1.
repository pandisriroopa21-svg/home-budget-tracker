
USE home_budget;

-- 1. View all transactions with category names
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
ORDER BY t.transaction_date;

-- 2. Total income
SELECT COALESCE(SUM(amount), 0) AS total_income
FROM transactions
WHERE transaction_type = 'Income';

-- 3. Total expenses
SELECT COALESCE(SUM(amount), 0) AS total_expenses
FROM transactions
WHERE transaction_type = 'Expense';

-- 4. Total savings
SELECT
    COALESCE(SUM(CASE
        WHEN transaction_type = 'Income' THEN amount
        ELSE -amount
    END), 0) AS total_savings
FROM transactions;

-- 5. Category-wise expenses for October 2026
SELECT
    c.category_name,
    SUM(t.amount) AS total_expenses
FROM transactions t
JOIN categories c
    ON t.category_id = c.category_id
WHERE t.transaction_type = 'Expense'
  AND t.transaction_date >= '2026-10-01'
  AND t.transaction_date < '2026-11-01'
GROUP BY c.category_id, c.category_name
ORDER BY total_expenses DESC;

-- 6. Monthly income and expenses
SELECT
    YEAR(transaction_date) AS year,
    MONTH(transaction_date) AS month,
    SUM(CASE WHEN transaction_type = 'Income'
        THEN amount ELSE 0 END) AS income,
    SUM(CASE WHEN transaction_type = 'Expense'
        THEN amount ELSE 0 END) AS expenses
FROM transactions
GROUP BY YEAR(transaction_date), MONTH(transaction_date)
ORDER BY year, month;

-- 7. Find categories exceeding their monthly budgets
SELECT
    c.category_name,
    b.budget_amount,
    COALESCE(SUM(t.amount), 0) AS amount_spent,
    COALESCE(SUM(t.amount), 0) - b.budget_amount AS overspent
FROM monthly_budgets b
JOIN categories c
    ON c.category_id = b.category_id
LEFT JOIN transactions t
    ON t.category_id = b.category_id
    AND t.transaction_type = 'Expense'
    AND YEAR(t.transaction_date) = b.budget_year
    AND MONTH(t.transaction_date) = b.budget_month
WHERE b.budget_month = 10
  AND b.budget_year = 2026
GROUP BY c.category_id, c.category_name, b.budget_amount
HAVING COALESCE(SUM(t.amount), 0) > b.budget_amount;
