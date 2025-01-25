import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

mydb = pymysql.connect(
  host="localhost",
  user="root",
  password="sql_1234h",
  database="expenses_tracker"
)

mycursor = mydb.cursor()

# Streamlit app title
st.title("SQL-Based Data Visualizations")

# Option list for the queries
option = [
    "1. Total Spending by Category in All Months",
    "2. Monthly Spending Trends",
    "3. Spending by Payment Mode",
    "4. Total Cashback Earned",
    "5. Top 5 Spending Categories",
    "6. Highest Spending Month",
    "7. Spending Breakdown by Day of the Week",
    "8. Average Spending Per Transaction",
    "9. Spending by Category and Month",
    "10. Spending by Payment Mode and Month",
    "11. Spending Distribution Across Categories (Boxplot)",
    "12. Spending Count by Payment Mode",
    "13. Average Spending in All Months",
    "14. Total Cashback by Payment Mode",
    "15. Total Spending on Bills in May",
    "16. Spending by Category in the Last 5 Days of year",
    "17. Food Spending Across All Months",
    "18. Spending by Category with Cashback",
    "19. Entertainment Spending Across All Months",
    "20. Average Spending by Category",
    "21. Highest Spending Categories in December",
    "22. Spending by Category and Payment Mode",
    "23. Highest Spending Categories in January",
    "24. Average Cashback by Payment Mode",
    "25. Monthly Cashback Earned",
    "26. December Spending",
    "27. Average Spending Per Transaction by Category",
    "28. Monthly Average Spending",
    "29. Spending by Category Over Time",
    "30. Average Spending Per Transaction by Category"
]

# Dropdown to select query
dv=st.selectbox("choose a option",option)
st.write(dv)

# Execute queries based on the selected option
if dv == "1. Total Spending by Category in All Months":
    st.subheader("Total Spending by Category in All Months")
    
    query = """
    SELECT category, MONTH(date) AS month, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY category, MONTH(date)
    ORDER BY category, month;
    """
    category_data = pd.read_sql(query, mydb)
    category_data = category_data.dropna(subset=['category', 'total_spent'])
    
    # Create a bar chart for total spending by category in all months
    # Reset index to use 'category' for x-axis and 'total_spent' for y-axis
    category_data['month'] = category_data['month'].astype(str)  # Make month a string for proper labeling
    st.bar_chart(category_data.set_index(['category', 'month'])['total_spent'].unstack(fill_value=0))
    
    # Display the raw data table
    st.write(category_data)


elif dv=="2. Monthly Spending Trends":
    # 2. Monthly Spending Trends (Line chart)
    st.subheader("Monthly Spending Trends")
    query = """
    SELECT MONTH(date) AS month, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY MONTH(date)
    ORDER BY month;
    """
    monthly_data = pd.read_sql(query, mydb)
    st.line_chart(monthly_data.set_index('month')['total_spent'])
    st.write(monthly_data)

elif dv == "3. Spending by Payment Mode":
    st.subheader("Spending by Payment Mode")
    query = """
    SELECT payment_mode, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY payment_mode;
    """
    payment_mode_data = pd.read_sql(query, mydb)
    fig, ax = plt.subplots()
    ax.pie(payment_mode_data['total_spent'], labels=payment_mode_data['payment_mode'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)
    st.write(payment_mode_data)

# 4. Total Cashback Earned (Metric)
elif dv == "4. Total Cashback Earned":
    st.subheader("Total Cashback Earned")
    query = """
    SELECT SUM(cashback) AS total_cashback
    FROM expenses
    WHERE cashback > 0;
    """
    cashback_data = pd.read_sql(query, mydb)
    st.metric(label="Total Cashback Earned", value=f"${cashback_data['total_cashback'][0]:,.2f}")
    st.write(cashback_data)

# 5. Top 5 Spending Categories (Table)
elif dv == "5. Top 5 Spending Categories":
    st.subheader("Top 5 Spending Categories")
    query = """
    SELECT category, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY category
    ORDER BY total_spent DESC
    LIMIT 5;
    """
    top_categories_data = pd.read_sql(query, mydb)
    st.write(top_categories_data)

# 6. Highest Spending Month (Table)
elif dv == "6. Highest Spending Month":
    st.subheader("Highest Spending Month (Considering Year)")
    query = """
    SELECT EXTRACT(YEAR FROM date) AS year, EXTRACT(MONTH FROM date) AS month, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date)
    ORDER BY total_spent DESC
    LIMIT 1;
    """
    highest_month_year_data = pd.read_sql(query, mydb)
    st.write(highest_month_year_data)

# 7. Spending Breakdown by Day of the Week (Bar Chart)
elif dv == "7. Spending Breakdown by Day of the Week":
    st.subheader("Spending Breakdown by Day of the Week")
    query = """
    SELECT DAYNAME(date) AS day, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY day
    ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');
    """
    day_of_week_data = pd.read_sql(query, mydb)
    st.bar_chart(day_of_week_data.set_index('day')['total_spent'])
    st.write(day_of_week_data)

# 8. Average Spending Per Transaction (Metric)
elif dv == "8. Average Spending Per Transaction":
    st.subheader("Average Spending Per Transaction")
    query = """
    SELECT AVG(amount_paid) AS avg_spent
    FROM expenses;
    """
    avg_spent_data = pd.read_sql(query, mydb)
    st.metric(label="Average Transaction Amount", value=f"${avg_spent_data['avg_spent'][0]:,.2f}")
    st.write(avg_spent_data)

# 9. Spending by Category and Month (Stacked Bar Chart)
elif dv == "9. Spending by Category and Month":
    st.subheader("Spending by Category and Month (Considering Year)")
    query = """
    SELECT 
        EXTRACT(YEAR FROM date) AS year,
        EXTRACT(MONTH FROM date) AS month,
        category,
        SUM(amount_paid) AS total_spent
    FROM 
        expenses
    GROUP BY 
        EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date), category
    ORDER BY 
        year, month;
    """
    category_month_data = pd.read_sql(query, mydb)
    category_month_data['year_month'] = (
        category_month_data['year'].astype(str) + '-' + category_month_data['month'].astype(str)
    )
    category_month_pivot = category_month_data.pivot(index='year_month', columns='category', values='total_spent')
    st.bar_chart(category_month_pivot)
    st.write(category_month_data)

# 10. Spending by Payment Mode and Month (Stacked Bar Chart)
elif dv == "10. Spending by Payment Mode and Month":
    st.subheader("Spending by Payment Mode and Month (Stacked Bar Chart)")
    query = """
    SELECT EXTRACT(MONTH FROM date) AS month, payment_mode, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY EXTRACT(MONTH FROM date), payment_mode
    ORDER BY EXTRACT(MONTH FROM date);
    """
    payment_mode_month_data = pd.read_sql(query, mydb)
    payment_mode_month_pivot = payment_mode_month_data.pivot(index='month', columns='payment_mode', values='total_spent')
    st.bar_chart(payment_mode_month_pivot)
    st.write(payment_mode_month_data)

# 11. Spending Distribution Across Categories (Boxplot)
elif dv == "11. Spending Distribution Across Categories (Boxplot)":
    st.subheader("Spending Distribution Across Categories (Boxplot)")
    query = """
    SELECT category, amount_paid
    FROM expenses;
    """
    category_spend_data = pd.read_sql(query, mydb)
    # Create a boxplot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='category', y='amount_paid', data=category_spend_data, ax=ax)
    ax.set_title("Spending Distribution Across Categories")
    ax.set_xlabel("Category")
    ax.set_ylabel("Amount Paid")
    st.pyplot(fig)
    st.write(category_spend_data)
# 12. Spending Count by Payment Mode (Bar Chart)
elif dv == "12. Spending Count by Payment Mode":
    st.subheader("Spending Count by Payment Mode")
    query = """
    SELECT payment_mode, COUNT(*) AS transaction_count
    FROM expenses
    GROUP BY payment_mode
    ORDER BY transaction_count DESC;
    """
    payment_mode_count_data = pd.read_sql(query, mydb)
    st.bar_chart(payment_mode_count_data.set_index('payment_mode')['transaction_count'])
    st.write(payment_mode_count_data)

# 13. Average Spending on Bills per Month
elif dv == "13. Average Spending in All Months":
    st.subheader("Average Spending in All Months")
    
    query = """
    SELECT MONTH(date) AS month, AVG(amount_paid) AS avg_spent
    FROM expenses
    GROUP BY MONTH(date)
    ORDER BY month;
    """
    avg_spending_data = pd.read_sql(query, mydb)
    
    # Create a line chart for average spending per month
    st.line_chart(avg_spending_data.set_index('month')['avg_spent'])
    
    # Display the raw data table
    st.write(avg_spending_data)

# 14. Total Cashback by Payment Mode (Pie Chart)
elif dv == "14. Total Cashback by Payment Mode":
    st.subheader("Total Cashback by Payment Mode")
    query = """
    SELECT payment_mode, SUM(cashback) AS total_cashback
    FROM expenses
    WHERE cashback > 0
    GROUP BY payment_mode;
    """
    cashback_by_payment_mode_data = pd.read_sql(query, mydb)
    fig, ax = plt.subplots()
    ax.pie(cashback_by_payment_mode_data['total_cashback'], labels=cashback_by_payment_mode_data['payment_mode'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)
    st.write(cashback_by_payment_mode_data)

# 15. Total Spending on Bills in May
elif dv == "15. Total Spending on Bills in May":
    st.subheader("Total Spending on Bills in May")
    
    query = """
    SELECT SUM(amount_paid) AS total_spent
    FROM expenses
    WHERE category = 'Bills' AND EXTRACT(MONTH FROM date) = 5;
    """
    bills_spending_data = pd.read_sql(query, mydb)
    total_spent = bills_spending_data['total_spent'][0] if bills_spending_data['total_spent'][0] is not None else 0
    st.metric(label="Total Spending on Bills in May", value=f"${total_spent:,.2f}")
    st.write(bills_spending_data)

# 16. Spending by Category in the Last 5 Days of year
elif dv == "16. Spending by Category in the Last 5 Days of year":
    st.subheader("Spending by Category in the Last 5 Days of year")
    
    query = """
    SELECT category, SUM(amount_paid) AS total_spent
    FROM expenses
    WHERE date BETWEEN '2023-12-27' AND '2023-12-31'
    GROUP BY category
    ORDER BY total_spent DESC;
    """
    last_5_days_year_data = pd.read_sql(query, mydb)
    st.bar_chart(last_5_days_year_data.set_index('category')['total_spent'])
    st.write(last_5_days_year_data)


# 17. Food Spending Across All Months
elif dv == "17. Food Spending Across All Months":
    st.subheader("Food Spending Across All Months")
    query = """
    SELECT EXTRACT(MONTH FROM date) AS month, SUM(amount_paid) AS total_food_spent
    FROM expenses
    WHERE category = 'Food'
    GROUP BY EXTRACT(MONTH FROM date)
    ORDER BY EXTRACT(MONTH FROM date);
    """
    food_spending_data = pd.read_sql(query, mydb)
    st.bar_chart(food_spending_data.set_index('month')['total_food_spent'])
    st.write(food_spending_data)

# 18. Spending by Category with Cashback (Bar Chart)
elif dv == "18. Spending by Category with Cashback":
    st.subheader("Spending by Category with Cashback")
    query = """
    SELECT category, SUM(amount_paid) AS total_spent, SUM(cashback) AS total_cashback
    FROM expenses
    WHERE cashback > 0
    GROUP BY category
    ORDER BY total_spent DESC;
    """
    category_cashback_data = pd.read_sql(query, mydb)
    # Create a bar chart for total spending
    st.subheader("Total Spending by Category with Cashback (Bar Chart)")
    st.bar_chart(category_cashback_data.set_index('category')['total_spent'])
    # Create a bar chart for total cashback
    st.subheader("Total Cashback by Category (Bar Chart)")
    st.bar_chart(category_cashback_data.set_index('category')['total_cashback'])
    st.write(category_cashback_data)

# 19. Entertainment Spending Across All Months
elif dv == "19. Entertainment Spending Across All Months":
    st.subheader("Entertainment Spending Across All Months")
    query = """
    SELECT EXTRACT(MONTH FROM date) AS month, SUM(amount_paid) AS total_entertainment_spent
    FROM expenses
    WHERE category = 'Entertainment'
    GROUP BY EXTRACT(MONTH FROM date)
    ORDER BY EXTRACT(MONTH FROM date);
    """
    entertainment_spending_data = pd.read_sql(query, mydb)
    st.bar_chart(entertainment_spending_data.set_index('month')['total_entertainment_spent'])
    st.write(entertainment_spending_data)

# 20. Average Spending by Category (Metric)
elif dv == "20. Average Spending by Category":
    st.subheader("Average Spending by Category")
    query = """
    SELECT category, AVG(amount_paid) AS avg_spent
    FROM expenses
    GROUP BY category
    ORDER BY avg_spent DESC;
    """
    avg_spending_category_data = pd.read_sql(query, mydb)
    st.bar_chart(avg_spending_category_data.set_index('category')['avg_spent'])
    st.write(avg_spending_category_data)

# 21. Highest Spending Categories in December
elif dv == "21. Highest Spending Categories in December":
    st.subheader("Highest Spending Categories in December (Line Chart)")
    
    query = """
    SELECT category, SUM(amount_paid) AS total_spent
    FROM expenses
    WHERE EXTRACT(MONTH FROM date) = 12
    GROUP BY category
    ORDER BY total_spent DESC
    LIMIT 5;
    """
    highest_spending_categories_december = pd.read_sql(query, mydb)
    st.line_chart(highest_spending_categories_december.set_index('category')['total_spent'])
    st.write(highest_spending_categories_december)

# 22. Spending by Category and Payment Mode (Stacked Bar Chart)
elif dv == "22. Spending by Category and Payment Mode":
    st.subheader("Spending by Category and Payment Mode (Stacked Bar Chart)")
    query = """
    SELECT category, payment_mode, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY category, payment_mode
    ORDER BY category;
    """
    category_payment_data = pd.read_sql(query, mydb)
    category_payment_pivot = category_payment_data.pivot(index='category', columns='payment_mode', values='total_spent')
    st.bar_chart(category_payment_pivot)
    st.write(category_payment_data)

# 23. Highest Spending Categories in January
elif dv == "23. Highest Spending Categories in January":
    st.subheader("Highest Spending Categories in January (Bar Chart)")
    
    query = """
    SELECT category, SUM(amount_paid) AS total_spent
    FROM expenses
    WHERE EXTRACT(MONTH FROM date) = 1
    GROUP BY category
    ORDER BY total_spent DESC
    LIMIT 5;
    """
    highest_spending_categories = pd.read_sql(query, mydb)
    st.bar_chart(highest_spending_categories.set_index('category')['total_spent'])
    st.write(highest_spending_categories)

# 24. Average Cashback by Payment Mode (Metric)
elif dv == "24. Average Cashback by Payment Mode":
    st.subheader("Average Cashback by Payment Mode (Bar Chart)")
    query = """
    SELECT payment_mode, AVG(cashback) AS avg_cashback
    FROM expenses
    WHERE cashback > 0
    GROUP BY payment_mode
    ORDER BY avg_cashback DESC;
    """
    avg_cashback_data = pd.read_sql(query, mydb)
    st.bar_chart(avg_cashback_data.set_index('payment_mode')['avg_cashback'])
    st.write(avg_cashback_data)

# 25. Monthly Cashback Earned (Bar Chart)
elif dv == "25. Monthly Cashback Earned":
    st.subheader("Monthly Cashback Earned (Line Chart)")
    query = """
    SELECT EXTRACT(MONTH FROM date) AS month, SUM(cashback) AS total_cashback
    FROM expenses
    WHERE cashback > 0
    GROUP BY EXTRACT(MONTH FROM date)
    ORDER BY month;
    """
    monthly_cashback_data = pd.read_sql(query, mydb)
    st.line_chart(monthly_cashback_data.set_index('month')['total_cashback'])
    st.write(monthly_cashback_data)

# 26. December Spending
elif dv == "26. December Spending":
    st.subheader("Spending in December (Category-wise)")
    
    # Query to get category-wise spending for December (Month 12)
    query_category = """
    SELECT category, SUM(amount_paid) AS total_spent
    FROM expenses
    WHERE EXTRACT(MONTH FROM date) = 12
    GROUP BY category
    ORDER BY total_spent DESC;
    """
    category_spending_data = pd.read_sql(query_category, mydb)
    
    # Create a bar chart for category-wise spending in December
    st.bar_chart(category_spending_data.set_index('category')['total_spent'])
    
    # Display the raw data table for category-wise spending in December
    st.write(category_spending_data)
        
# 27. Average Spending Per Transaction by Category
elif dv == "27. Average Spending Per Transaction by Category":
    st.subheader("Average Spending Per Transaction by Category")
    query = """
    SELECT category, AVG(amount_paid) AS avg_spent
    FROM expenses
    GROUP BY category
    ORDER BY avg_spent DESC;
    """
    avg_spent_category_data = pd.read_sql(query, mydb)
    st.bar_chart(avg_spent_category_data.set_index('category')['avg_spent'])
    st.write(avg_spent_category_data)

# 28. Monthly Average Spending (Metric)
elif dv == "28. Monthly Average Spending":
    st.subheader("Monthly Average Spending (Line Chart)")
    query = """
    SELECT EXTRACT(MONTH FROM date) AS month, AVG(amount_paid) AS avg_spent
    FROM expenses
    GROUP BY EXTRACT(MONTH FROM date)
    ORDER BY month;
    """
    monthly_avg_spending_data = pd.read_sql(query, mydb)
    st.line_chart(monthly_avg_spending_data.set_index('month')['avg_spent'])
    st.write(monthly_avg_spending_data)

# 29. Spending by Category Over Time (Line Chart)
elif dv == "29. Spending by Category Over Time":
    st.subheader("Spending by Category Over Time (Line Chart)")
    query = """
    SELECT DATE(date) AS spending_date, category, SUM(amount_paid) AS total_spent
    FROM expenses
    GROUP BY spending_date, category
    ORDER BY spending_date;
    """
    category_over_time_data = pd.read_sql(query, mydb)
    category_over_time_pivot = category_over_time_data.pivot(index='spending_date', columns='category', values='total_spent')
    st.line_chart(category_over_time_pivot)
    st.write(category_over_time_data)

# 30. Average Spending Per Transaction by Category
elif dv == "30. Average Spending Per Transaction by Category":
    st.subheader("Average Spending Per Transaction by Category")
    query = """
    SELECT category, AVG(amount_paid) AS avg_spent_per_transaction
    FROM expenses
    GROUP BY category
    ORDER BY avg_spent_per_transaction DESC;
    """
    avg_spent_category_data = pd.read_sql(query, mydb)

    # Create a bar chart for average spending per transaction by category
    st.bar_chart(avg_spent_category_data.set_index('category')['avg_spent_per_transaction'])

    # Display raw data table
    st.write(avg_spent_category_data)