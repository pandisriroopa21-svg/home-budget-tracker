
USE home_budget;

INSERT INTO categories (category_name, category_type)
VALUES
('Salary', 'Income'),
('Business', 'Income'),
('Groceries', 'Expense'),
('Rent', 'Expense'),
('Transportation', 'Expense'),
('Healthcare', 'Expense'),
('Education', 'Expense'),
('Entertainment', 'Expense');

INSERT INTO transactions
(transaction_date, transaction_type, category_id, amount, description)
VALUES
('2026-10-01', 'Income', 1, 50000, 'Monthly Salary'),
('2026-10-02', 'Expense', 3, 8000, 'Groceries'),
('2026-10-03', 'Expense', 4, 12000, 'House Rent'),
('2026-10-04', 'Expense', 5, 3000, 'Transportation'),
('2026-10-05', 'Expense', 7, 5000, 'Education'),
('2026-10-06', 'Expense', 6, 2000, 'Healthcare'),
('2026-10-07', 'Expense', 8, 4000, 'Entertainment');

INSERT INTO monthly_budgets
(category_id, budget_month, budget_year, budget_amount)
VALUES
(3, 10, 2026, 7000),
(4, 10, 2026, 12000),
(5, 10, 2026, 4000),
(6, 10, 2026, 3000),
(7, 10, 2026, 6000),
(8, 10, 2026, 3000);
