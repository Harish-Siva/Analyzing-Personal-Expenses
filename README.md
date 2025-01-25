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
