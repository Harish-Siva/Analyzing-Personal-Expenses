import pandas as pd
import random
from faker import Faker
import calendar

# Initialize the Faker instance
fake = Faker()

# Define categories with corresponding plausible descriptions
category_descriptions = {
    'Food': [
        'Pizza order',
        'Grocery shopping at local market',
        'Dinner at Italian restaurant',
        'Coffee at cafe',
        'Bakery purchase'
    ],
    'Transportation': [
        'Taxi fare',
        'Monthly bus pass',
        'Train ticket to downtown',
        'Gas station refill',
        'Ride-sharing service payment'
    ],
    'Bills': [
        'Electricity bill payment',
        'Water utility bill',
        'Internet service provider charge',
        'Mobile phone bill',
        'Cable TV subscription'
      ],
    'Entertainment': [
        'Movie theater ticket',
        'Concert ticket purchase',
        'Streaming service subscription',
        'Amusement park entry fee',
        'Bookstore purchase'
    ],
    'Healthcare': [
        'Pharmacy medication purchase',
        'Doctor consultation fee',
        'Dental clinic payment',
        'Health insurance premium',
        'Optician eyewear purchase'
    ],
    'Groceries': [
        'Dairy products',
        'Meat and fish',
        'Kitchen items',
        'Snacks and Drinks',
        'Cooking Essentials'
    ],
    'Subscriptions': [
        'Amazon Prime Membership',
        'Netflix',
        'Spotify',
        'LinkedIn',
        'Disney Hotstar'
    ]
}

# Define cashback rates based on payment mode
cashback_rates = {
    'UPI': 0.05,     # 5% cashback for UPI
    'Online': 0.10,  # 10% cashback for Online
    # Other payment modes can have 0% cashback or specified rates
    'Cash': 0.15,
    'CardTransaction': 0.05,
    'Netbanking': 0.05
}

# Function to generate random dates within a specific month and year
def generate_random_dates(year, month, num_records):
    # Determine the number of days in the month
    num_days = pd.Period(year=year, month=month, freq='M').days_in_month
    
    if num_records <= num_days:
        # Generate unique random days within the month
        days = random.sample(range(1, num_days + 1), num_records)
    else:
        # Allow duplicates if num_records exceeds num_days
        days = [random.randint(1, num_days) for _ in range(num_records)]
    
    # Create dates for the specified month and year
    dates = [f"{year}-{month:02d}-{day:02d}" for day in days]
    return dates

# Function to generate monthly expense data
def generate_monthly_data(year, month, num_records):
    dates = generate_random_dates(year, month, num_records)
    categories = list(category_descriptions.keys())
    payment_modes = list(cashback_rates.keys())
    
    data = {
        'Date': dates,
        'Category': [],
        'Payment Mode': [],
        'Description': [],
        'Amount Paid': [],
        'Cashback': []
    }
    
    for _ in range(num_records):
        category = random.choice(categories)
        payment_mode = random.choice(payment_modes)
        description = random.choice(category_descriptions[category])
        amount_paid = round(random.uniform(10, 500), 2)
        cashback = round(amount_paid * cashback_rates[payment_mode], 2)
        
        data['Category'].append(category)
        data['Payment Mode'].append(payment_mode)
        data['Description'].append(description)
        data['Amount Paid'].append(amount_paid)
        data['Cashback'].append(cashback)
    
    return pd.DataFrame(data)

# Dictionary to store DataFrames for each month
monthly_dataframes = {}

# Generate and store data for each month
for month in range(1, 13):
    # Generate data for the current month
    monthly_data = generate_monthly_data(2023, month, num_records=180)
    
    # Add the month name column for clarity
    monthly_data['Month'] = calendar.month_name[month]
    
    # Store the DataFrame in the dictionary using the month name as the key
    monthly_dataframes[calendar.month_name[month]] = monthly_data

# Example: Accessing and displaying the first few rows of January's data
print(monthly_dataframes['January'].head())

import os

# Ensure the directory to save CSV files exists
output_dir = 'expense_data'
os.makedirs(output_dir, exist_ok=True)

# Iterate over each month's DataFrame in the dictionary
for month_name, month_data in monthly_dataframes.items():
    # Define the file path for the CSV file
    file_path = os.path.join(output_dir, f'{month_name}_2023.csv')
    
    # Save the DataFrame to a CSV file
    month_data.to_csv(file_path, index=False, encoding='utf-8')
    
    print(f'Saved {month_name} data to {file_path}')

import mysql.connector

# Create a new database and table if they do not exist
def create_database_and_table():
    connection = create_mysql_connection()
    cursor = connection.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS expenses_db")
    cursor.execute("USE expenses_db")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            date DATE,
            category VARCHAR(255),
            payment_mode VARCHAR(255),
            description VARCHAR(255),
            amount_paid FLOAT,
            cashback FLOAT,
            month VARCHAR(255)
        )
    ''')

    connection.commit()
    cursor.close()
    connection.close()

# Function to insert data into MySQL database
def insert_data_into_mysql(month_data):
    try:
        import pymysql
        
        mydb=pymysql.connect(
        host="localhost",         # Your MySQL server host (use 'localhost' if running locally)
        user="root",     # Your MySQL username
        password="sql_1234h", # Your MySQL password
        database="expenses_tracker" # The database name to connect to (you can create one before)
    )
        cursor = mydb.cursor()

        insert_query = '''
        INSERT INTO expenses (date, category, payment_mode, description, amount_paid, cashback, month)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''

        for _, row in month_data.iterrows():
            cursor.execute(insert_query, (
                row['Date'], row['Category'], row['Payment Mode'], row['Description'],
                row['Amount Paid'], row['Cashback'], row['Month']
            ))

        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
# Insert all monthly data into the database
for month_name, month_data in monthly_dataframes.items():
    insert_data_into_mysql(month_data)
    print(f'Data for {month_name} inserted into MySQL database')

import pymysql
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

mydb = pymysql.connect(
  host="localhost",
  user="root",
  password="sql_1234h",
  database="expenses_tracker"
)

mycursor = mydb.cursor()

# Query the database to fetch data
mycursor.execute("SELECT DISTINCT * FROM expenses")
myresult = mycursor.fetchall()

# Get column names from the cursor description
columns = [col[0] for col in mycursor.description]
# Close the cursor and connection
mycursor.close()

# Convert the data to a pandas DataFrame
df = pd.DataFrame(myresult, columns=columns)

# Display the first few rows of the DataFrame
print(df.tail())

# 1.Number of Observations and Variables
print(f"Observations (Rows): {df.shape[0]}")
print(f"Variables (Columns): {df.shape[1]}")

# Data Types of Each Column
print("\nData Types:")
print(df.dtypes)

# Basic Statistics
print("\nBasic Statistics:")
print(df.describe(include='all'))

#2. Categorize variables into categorical and numerical
categorical_columns = df.select_dtypes(include=['object']).columns
numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns

print(f"Categorical Columns: {list(categorical_columns)}")
print(f"Numerical Columns: {list(numerical_columns)}")

# Check distributions
for col in numerical_columns:
    sns.histplot(df[col], kde=True)
    plt.title(f'Distribution of {col}')
    plt.show()

for col in categorical_columns:
    print(f"\n{col} Value Counts:")
    print(df[col].value_counts())

#3. Pairplot for relationships
sns.pairplot(df)
plt.show()

# Correlation heatmap
correlation_matrix = df[numerical_columns].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title("Correlation Between Numerical Variables")
plt.show()

from scipy.stats import zscore

#4. Calculate Z-scores for numerical columns
z_scores = df[numerical_columns].apply(zscore)

# Identify outliers based on Z-scores (>3 or <-3)
outliers = (z_scores > 3) | (z_scores < -3)
print("\nOutliers Detected (Per Column):")
print(outliers.sum())

# Visualize outliers using boxplots
for col in numerical_columns:
    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df, x=col)
    plt.title(f'Boxplot for {col}')
    plt.show()

#5. Check for missing values
print("\nMissing Values Per Column:")
print(df.isnull().sum())

# Visualize missing values
plt.figure(figsize=(8, 6))
sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
plt.title('Heatmap of Missing Values')
plt.show()

#6. Check for duplicate rows
duplicate_count = df.duplicated().sum()
print("\nNumber of Duplicate Rows:", duplicate_count)

# Remove duplicates if necessary
df = df.drop_duplicates()
print("Duplicates removed. Updated row count:", df.shape[0])

#7. Ensure 'date' column is in datetime format
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

    # Extract year and month
    df['year_month'] = df['date'].dt.to_period('M')

    # Plot trends over time
    if 'amount' in df.columns:
        monthly_expenses = df.groupby('year_month')['amount'].sum()
        monthly_expenses.plot(kind='line', marker='o', figsize=(10, 6))
        plt.title("Monthly Expense Trends")
        plt.xlabel("Year-Month")
        plt.ylabel("Total Amount")
        plt.grid()
        plt.show()

#8. Variability (standard deviation) in numerical columns
print("\nVariability (Standard Deviation) for Numerical Columns:")
print(df[numerical_columns].std())

# Coefficient of variation (CV) for numerical columns
cv = (df[numerical_columns].std() / df[numerical_columns].mean()) * 100
print("\nCoefficient of Variation (%):")
print(cv)

#9. Example: Compare actual expenses with expected budget (if applicable)
if 'amount' in df.columns and 'budget' in df.columns:
    df['difference'] = df['amount'] - df['budget']
    print("\nDifferences Between Actual and Budgeted Amounts:")
    print(df[['amount', 'budget', 'difference']].head())
    
    # Visualize discrepancies
    plt.figure(figsize=(8, 6))
    sns.histplot(df['difference'], kde=True, color='red')
    plt.title("Distribution of Differences (Actual vs. Budget)")
    plt.show()

#10. Grouping by 'category' and calculating the mean of 'amount_paid'
if 'category' in df.columns and 'amount_paid' in df.columns:
    category_summary = df.groupby('category')['amount_paid'].mean()
    print("\nAverage Amount Paid by Category:")
    print(category_summary)

    # Visualize the average amount paid by category
    category_summary.plot(kind='bar', figsize=(10, 6), color='teal')
    plt.title("Average Expense by Category")
    plt.xlabel("Category")
    plt.ylabel("Average Amount Paid")
    plt.xticks(rotation=45)
    plt.show()
else:
    print("Either 'category' or 'amount_paid' column is missing.")

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
