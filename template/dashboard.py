
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Home Budget Tracker | Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>

<div class="container">

    <header class="dashboard-header">
        <div>
            <h1>Home Budget Tracker</h1>
            <p>Manage your money. Plan your future.</p>
        </div>
        <div class="header-icon">₹</div>
    </header>

    <!-- Navigation -->
    <nav class="navbar">
        <a href="{{ url_for('home') }}" class="active">Dashboard</a>
        <a href="{{ url_for('add_transaction') }}">Add Transaction</a>
        <a href="{{ url_for('analysis') }}">Expense Analysis</a>
        <a href="{{ url_for('budget') }}">Monthly Budget</a>
        <a href="{{ url_for('transactions') }}">Transaction History</a>
    </nav>

    {% if request.args.get('added') %}
        <p class="message">Transaction added successfully!</p>
    {% endif %}

    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    <!-- Welcome Section -->
    <section class="welcome-section">
        <div>
            <h2>Welcome to your dashboard!</h2>
            <p>Here is an overview of your finances.</p>
        </div>
        <a class="primary-link" href="{{ url_for('add_transaction') }}">
            + Add Transaction
        </a>
    </section>

    <!-- Financial Summary -->
    <section class="cards">

        <div class="card income-card">
            <div class="card-top">
                <span class="card-label">Total Income</span>
                <span class="card-icon">↗</span>
            </div>
            <h2>₹{{ "%.2f"|format(income) }}</h2>
            <p>Money received</p>
        </div>

        <div class="card expense-card">
            <div class="card-top">
                <span class="card-label">Total Expenses</span>
                <span class="card-icon">↘</span>
            </div>
            <h2>₹{{ "%.2f"|format(expenses) }}</h2>
            <p>Money spent</p>
        </div>

        <div class="card balance-card">
            <div class="card-top">
                <span class="card-label">Remaining Balance</span>
                <span class="card-icon">₹</span>
            </div>
            <h2>₹{{ "%.2f"|format(income - expenses) }}</h2>
            <p>Income minus expenses</p>
        </div>

    </section>

    <!-- Quick Access -->
    <section class="panel">
        <h2>Quick Access</h2>
        <p class="section-description">
            Choose a section to manage and understand your finances.
        </p>

        <div class="quick-links">

            <a href="{{ url_for('add_transaction') }}" class="quick-link">
                <span class="quick-icon add-icon">＋</span>
                <span>
                    <strong>Add Transaction</strong>
                    <small>Record income or expenses</small>
                </span>
                <span class="arrow">›</span>
            </a>

            <a href="{{ url_for('analysis') }}" class="quick-link">
                <span class="quick-icon analysis-icon">▥</span>
                <span>
                    <strong>Expense Analysis</strong>
                    <small>Understand your spending</small>
                </span>
                <span class="arrow">›</span>
            </a>

            <a href="{{ url_for('budget') }}" class="quick-link">
                <span class="quick-icon budget-icon">◷</span>
                <span>
                    <strong>Monthly Budget</strong>
                    <small>Compare budgets and expenses</small>
                </span>
                <span class="arrow">›</span>
            </a>

            <a href="{{ url_for('transactions') }}" class="quick-link">
                <span class="quick-icon history-icon">☷</span>
                <span>
                    <strong>Transaction History</strong>
                    <small>Review recorded transactions</small>
                </span>
                <span class="arrow">›</span>
            </a>

        </div>
    </section>

    <!-- Footer -->
    <footer class="dashboard-footer">
        <p>Home Budget Tracker · Track wisely, save consistently.</p>
    </footer>

</div>

</body>
</html>
