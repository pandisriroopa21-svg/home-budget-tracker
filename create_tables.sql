
CREATE DATABASE IF NOT EXISTS home_budget;
USE home_budget;

CREATE TABLE IF NOT EXISTS categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    category_type ENUM('Income', 'Expense') NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_date DATE NOT NULL,
    transaction_type ENUM('Income', 'Expense') NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(100),
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
    CHECK (amount > 0)
);

CREATE TABLE IF NOT EXISTS monthly_budgets (
    budget_id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT NOT NULL,
    budget_month TINYINT NOT NULL,
    budget_year SMALLINT NOT NULL,
    budget_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
    UNIQUE (category_id, budget_month, budget_year),
    CHECK (budget_month BETWEEN 1 AND 12),
    CHECK (budget_amount >= 0)
);
