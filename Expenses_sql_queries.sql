SELECT * FROM expenses_tracker.expenses;
select * from expenses;
USE expenses_tracker;
SELECT DATABASE();
SHOW TABLES;
SHOW TABLES LIKE 'expenses%';
DESCRIBE expenses;

-- (1) What is the total amount spent in each category?
SELECT category, SUM(amount_paid) AS total_expenses
FROM expenses
GROUP BY category
ORDER BY total_expenses DESC;

-- (2) What is the total amount spent using each payment mode?
SELECT payment_mode, SUM(amount_paid) AS total_expenses
FROM expenses
GROUP BY payment_mode
ORDER BY total_expenses DESC;

-- (3) What is the total cashback received across all transactions?
SELECT SUM(cashback) AS total_cashback
FROM expenses;

-- (4) Which are the top 5 most expensive categories in terms of spending?
SELECT category, SUM(amount_paid) AS total_expenses
FROM expenses
GROUP BY category
ORDER BY total_expenses DESC
LIMIT 5;

-- (5) How much was spent on transportation using different payment modes?
SELECT payment_mode, SUM(amount_paid) AS total_expenses
FROM expenses
WHERE category = 'Transportation'
GROUP BY payment_mode
ORDER BY total_expenses DESC;

-- (6) Which transactions resulted in cashback?
SELECT *
FROM expenses
WHERE cashback > 0
ORDER BY cashback DESC;

-- (7) What is the total spending in each month of the year?
SELECT month, SUM(amount_paid) AS total_expenses
FROM expenses
GROUP BY month
ORDER BY FIELD(month, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December');

-- (8) Which months have the highest spending in categories like "Travel," "Entertainment," or "Gifts"?
SELECT 
    category, 
    month, 
    SUM(amount_paid) AS total_expenses
FROM 
    expenses
WHERE 
    category IN ('Travel', 'Entertainment', 'Gifts')
GROUP BY 
    category, month
ORDER BY 
    category, total_expenses DESC;

-- (9) Are there any recurring expenses during specific months of the year (e.g., insurance premiums, property taxes)?
SELECT 
    description, 
    month, 
    COUNT(*) AS occurrence_count, 
    SUM(amount_paid) AS total_expenses
FROM 
    expenses
WHERE 
    description LIKE 'Health insurance premium' OR 
    description LIKE 'Property tax payment'
GROUP BY 
    description, month
ORDER BY 
    description, occurrence_count DESC, total_expenses DESC;

-- (10) How much cashback or rewards were earned in each month?
SELECT 
    month, 
    SUM(cashback) AS total_cashback
FROM 
    expenses
GROUP BY 
    month
ORDER BY 
    FIELD(month, 'January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December');

-- (11) How has your overall spending changed over time (e.g., increasing, decreasing, remaining stable)?
WITH MonthlySpending AS (
    SELECT 
        FIELD(month, 'January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December') AS month_order,
        month,
        SUM(amount_paid) AS total_expenses
    FROM 
        expenses
    GROUP BY 
        month
    ORDER BY 
        month_order
),
SpendingTrends AS (
    SELECT 
        month,
        total_expenses,
        LAG(total_expenses) OVER (ORDER BY month_order) AS previous_month_spent,
        CASE 
            WHEN total_expenses > LAG(total_expenses) OVER (ORDER BY month_order) THEN 'Increasing'
            WHEN total_expenses < LAG(total_expenses) OVER (ORDER BY month_order) THEN 'Decreasing'
            ELSE 'Stable'
        END AS spending_trend
    FROM 
        MonthlySpending
)
SELECT 
    month, 
    total_expenses, 
    previous_month_spent, 
    spending_trend
FROM 
    SpendingTrends;

-- (12) What are the typical costs associated with different types of travel (e.g., flights, accommodation, transportation)?
SELECT 
    description, 
    category,
    AVG(amount_paid) AS average_cost,
    MIN(amount_paid) AS minimum_cost,
    MAX(amount_paid) AS maximum_cost,
    COUNT(*) AS transaction_count
FROM 
    expenses
WHERE 
    category = 'Travel'
GROUP BY 
    description, category
ORDER BY 
    category, average_cost DESC;

-- (13) Are there any patterns in grocery spending (e.g., higher spending on weekends, increased spending during specific seasons)?
SELECT 
    CASE 
        WHEN DAYOFWEEK(date) IN (1, 7) THEN 'Weekend' 
        ELSE 'Weekday' 
    END AS day_type,
    SUM(amount_paid) AS total_expenses,
    COUNT(*) AS transaction_count
FROM 
    expenses
WHERE 
    category = 'Groceries'
GROUP BY 
    day_type
ORDER BY 
    total_expenses DESC;

-- (14) Define High and Low Priority Categories
SELECT 
    category, 
    SUM(amount_paid) AS total_expenses, 
    COUNT(*) AS transaction_count,
    CASE 
        WHEN SUM(amount_paid) > (SELECT AVG(total_expenses) FROM 
                                 (SELECT SUM(amount_paid) AS total_expenses FROM expenses GROUP BY category) AS avg_spending) 
             THEN 'High Priority'
        ELSE 'Low Priority'
    END AS priority
FROM 
    expenses
GROUP BY 
    category
ORDER BY 
    total_expenses DESC;

-- (15) Which category contributes the highest percentage of the total spending?
SELECT 
    category, 
    SUM(amount_paid) AS total_expenses,
    (SUM(amount_paid) / (SELECT SUM(amount_paid) FROM expenses) * 100) AS percentage_of_total
FROM 
    expenses
GROUP BY 
    category
ORDER BY 
    percentage_of_total DESC
LIMIT 1;

-- (16) Transactions in a specific category (e.g., "Food")
SELECT *
FROM expenses
WHERE category = 'Food';

-- (17) Highest amount spent in a single transaction
SELECT MAX(amount_paid) AS highest_transaction
FROM expenses;

-- (18) Lowest amount spent in a single transaction
SELECT MIN(amount_paid) AS lowest_transaction
FROM expenses;

-- (19) Average spending per transaction
SELECT AVG(amount_paid) AS average_spending
FROM expenses;

-- (20) Count the number of transactions in each category
SELECT category, COUNT(*) AS total_transactions
FROM expenses
GROUP BY category;

-- (21) List transactions above a certain amount (e.g., $100)
SELECT *
FROM expenses
WHERE amount_paid > 100;

-- (22) Total spending by each payment mode for a specific category
SELECT payment_mode, SUM(amount_paid) AS total_spent
FROM expenses
WHERE category = 'Entertainment'
GROUP BY payment_mode;

-- (23) Find transactions on weekends
SELECT *
FROM expenses
WHERE DAYOFWEEK(date) IN (1, 7);

-- (24) List all unique payment modes used
SELECT DISTINCT payment_mode
FROM expenses;

-- (25) Total cashback earned for each category
SELECT category, SUM(cashback) AS total_cashback
FROM expenses
GROUP BY category;

-- (26) Transactions in a specific month (e.g., January)
SELECT *
FROM expenses
WHERE month = 'January';

-- (27) Transactions in a specific year (e.g., 2024)
SELECT *
FROM expenses
WHERE YEAR(date) = 2024;

-- (28) Total spending on utilities
SELECT SUM(amount_paid) AS total_spent
FROM expenses
WHERE category = 'Utilities';

-- (29) Count the number of cashbacks received
SELECT COUNT(*) AS cashback_transactions
FROM expenses
WHERE cashback > 0;

select * from expenses;



